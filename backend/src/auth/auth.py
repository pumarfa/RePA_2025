from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Librerias necesarias para la función get_current_user de validacion del usuario
from fastapi import Depends, HTTPException, status 
from sqlalchemy.orm import Session
from src.models.user_model import User
from fastapi.security import OAuth2PasswordBearer
from src.db.database import get_db

# Configuración de JWT
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") # Cambia esto a un valor seguro
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #os.getenv(ACCESS_TOKEN_EXPIRE_MINUTES)

# Objeto necesario para la función de 'get_current_user' que valida los datos del usuario
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# Generar un token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verificar y decodificar un token JWT
def verify_token(token: str):
    print(f"Token recibido: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload decodificado: {payload}")
        return payload
    except JWTError as e:
        print(f"Error al decodificar token: {e}")
        return None


# Dependencia para validar usuarios autenticados
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print (f"Usuario no encontrado: {user_id}")
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user