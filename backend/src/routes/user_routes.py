from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # PAra el debug de errores
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from src.auth.auth import create_access_token, verify_token, get_current_user # Se mueve la funcion 'get_current_user' a la libreria de 'auth'
from src.auth.permissions import has_role, has_user_role
from src.models.user_model import User, Role
from src.schemas.user_schema import UserCreate, UserOut, UserUpdate
from src.db.database import get_db
from datetime import datetime
from uuid import uuid4
import re

user_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

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


# Actualizar último acceso... Esto se debe integrar a la ruta de logín del usuario.
# @user_router.patch("/{email}/last-login", response_model=UserOut)
def update_last_login(email: str, db: Session = Depends(get_db), description="Actualiza en el registro de usuario, fecha y hora del login."):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    #return db_user

# Crear un usuario nuevo
@user_router.post("/register", response_model=UserOut, description="Crear un nuevo usuario")
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario con el rol "user" por defecto.
    """
     # Validar la contraseña
    validar_password(user_in.password)

    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )

    # Hashear la contraseña
    hashed_password = get_password_hash(user_in.password)

    # Crear el nuevo usuario
    new_user = User(
        id=str(uuid4()),  # Generar un UUID único
        email=user_in.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
    )

    # Asignar el rol "user" por defecto
    user_role = db.query(Role).filter(Role.rol == "user").first()
    if not user_role:
        # Si el rol "user" no existe, crearlo
        user_role = Role(rol="user")
        db.add(user_role)
        db.commit()
        db.refresh(user_role)

    # Asociar el rol al nuevo usuario
    new_user.roles.append(user_role)

    # Guardar el usuario en la base de datos
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Devolver el usuario creado
    return new_user

# Inicio de sesión [form_data: OAuth2PasswordRequestForm = Depends()]
@user_router.post("/login", description="Iniciar sesión")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Actualizar el último login
    user.last_login =  datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# Recuperar datos del usuario autenticado
@user_router.get("/me", response_model=UserOut, description="Obtener los datos del usuario logueado")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retorna datos del usuario autenticado.
    """
    return current_user

# Actualizar usuario (por ejemplo, cambiar contraseña)
@user_router.put("/me", response_model=UserOut, description="Actualizar los datos del usuario logueado")
def update_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Actualizar los datos del usuario logueado
    """
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = pwd_context.hash(user_update.password)
    db.commit()
    db.refresh(current_user)
    return current_user

# Eliminar un usuario siempre el el email del current:user sea igual al del token
@user_router.delete("/me", description="Eliminar un usuario, solo el propietario puede eliminar su cuenta. Set is_active=False")
def delete_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Cambiar estado de is_active True/False.
    Se establece el campo is_active en False para borrar el usuario.
    """
    if user_update.is_active:
        current_user.is_active = False
    else:
        current_user.is_active = True
    db.commit()
    db.refresh(current_user)
    return current_user

