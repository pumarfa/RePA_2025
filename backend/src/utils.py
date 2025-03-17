from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status 
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from src.models.user_models import User
from src.schemas.user_schemas import Token, UserUpdate
from src.database import get_db

# Librerias necesarias para la función get_current_user de validacion del usuario
from src.database import get_db

# Configuración de JWT
from dotenv import load_dotenv
import os
import re

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") # Cambia esto a un valor seguro
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = 30 #os.getenv(ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = 7 #os.getenv(REFRESH_TOKEN_EXPIRE_DAYS)

# Objeto necesario para la función de 'get_current_user' que valida los datos del usuario
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# Configuración de passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashear la contraseña
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Actualizar último acceso... Esto se debe integrar a la ruta de logín del usuario.
def update_last_login(email: str, db: Session = Depends(get_db), description="Actualiza en el registro de usuario, fecha y hora del login."):
    """
    Actualiza en el registro de usuario, fecha y hora del login.
    """
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_user)
    return db_user

# Validar el token de acceso
def verify_token(token: str, credentials_exception=HTTPException(status_code=401, detail="No autorizado", headers={"WWW-Authenticate":
"Bearer"})):
    """
    Verifica el token de acceso.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = Token(**payload)
    except JWTError:
        raise credentials_exception
    return token_data

# Decodificar el token de acceso
def decode_access_token(token: str):
    """
    Decodifica el token de acceso.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decode_Access_Token:Payload decodificado: {payload}") # Debug
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Validar el usuario
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Valida el token de acceso y retorna los datos del usuario.
    """
    payload = decode_access_token(token)
    user_data = {
        "id": payload.get("id"),
        "email": payload.get("email"),
        "is_active": payload.get("is_active"),
        "created_at": payload.get("created_at"),
        "last_login": payload.get("last_login"),
        "roles": payload.get("roles"),
        "type": payload.get("type")
    }
    return user_data

# Generar un token de acceso
def create_access_token(data: dict, expires_delta: timedelta = None, description="Generar un token JWT con los datos del usuario y una fecha de expiración opcional."):
    """
    Genera un access token con expiración corta.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE))
    # Se añade el tipo de token para distinguirlo en el refresh endpoint
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None, description="Generar un refresh token con expiración larga."):
    """
    Genera un refresh token con expiración larga.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(days=REFRESH_TOKEN_EXPIRE))
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validar_password(password: str):
    """
    Valida que la contraseña cumpla con los requisitos:
    - Mínimo 8 caracteres.
    - Al menos una letra mayúscula.
    - Al menos un número.
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres",
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra mayúscula",
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos un número",
        )

# Verifica si el usuario tiene al menos uno de los roles requeridos
def has_user_role(current_user: dict, required_roles: list[str]) -> bool:
    """
    Verifica si el usuario tiene al menos uno de los roles requeridos.
    
    Args:
        current_user (dict): Diccionario con los datos del usuario (incluyendo 'roles')
        required_roles (list[str]): Lista de roles requeridos (ej. ["admin", "editor"])
    
    Returns:
        bool: True si tiene al menos un rol requerido, False en caso contrario
    """
    
    if not current_user.get("is_active", False):
        return False
    
    # Extraer los roles del usuario en minúsculas
    user_roles = [role["rol"].lower() for role in current_user.get("roles", [])]
    
    # Convertir roles requeridos a minúsculas para comparación case-insensitive
    required_roles_lower = [r.lower() for r in required_roles]
    
    # Verificar coincidencias
    return any(role in required_roles_lower for role in user_roles)

# Verifica que el nuevo email no esté siendo usado por otro usuario
def verify_email_unique(db: Session, user_in: UserUpdate, current_user: dict):
    """
    Verifica que el nuevo email no esté siendo usado por otro usuario
    y que no pertenezca al usuario actual
    """
    # Si el email no cambió, no es necesario verificar
    if user_in.email == current_user["email"]:
        return
    
    # Buscar usuario con el email propuesto
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    
    # Si existe y pertenece a otro usuario, lanzar error
    if existing_user and existing_user.id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado por otro usuario"
        )