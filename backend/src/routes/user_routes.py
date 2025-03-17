from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # PAra el debug de errores
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from src.models.user_models import User, Role
from src.schemas.user_schemas import UserCreate, UserOut, UserUpdate
from src.database import get_db
from src.utils import get_password_hash, validar_password,update_last_login,create_access_token,create_refresh_token,get_current_user
from datetime import datetime, timezone
from uuid import uuid4

user_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crear un usuario nuevo# Crear un usuario nuevo
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
        created_at=datetime.now(timezone.utc),
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
@user_router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Iniciar sesión con un usuario registrado.
    """
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico o contraseña incorrectos",
        )
    
    # Verificar la contraseña
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico o contraseña incorrectos",
        )
    
    # Actualizar la fecha y hora del último acceso
    update_last_login(user.email, db)
    
    # Convertir usuario a formato UserOut compatible con JSON
    data_access = {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "roles": [{"id": role.id, "rol": role.rol} for role in user.roles],
        "type": "access"
    }
    
    data_refresh = {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "roles": [{"id": role.id, "rol": role.rol} for role in user.roles],
        "type": "refresh"
    }

    # Generar un token de acceso
    access_token = create_access_token(data=data_access)
    refresh_token = create_refresh_token(data=data_refresh)

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }
    
@user_router.get("/me", response_model=UserOut, description="Obtener datos del usuario actual")
def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Obtener los datos del usuario actual.
    """
    
    return current_user

# Actualizar usuario
@user_router.put("/me", response_model=UserUpdate, description="Actualizar los datos del usuario actual")
def update_user(user_in: UserUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Actualizar los datos del usuario actual.
    """
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado",
        )
    
    # Actualizar los datos del usuario
    if user_in.email:
        user.email = user_in.email # Actualizar el correo electrónico si se proporciona y no hay duplicados
    if user_in.password:
        validar_password(user_in.password)
        user.hashed_password = get_password_hash(user_in.password)
    
    # Guardar los cambios
    db.commit()
    db.refresh(user)
    
    # Devolver el usuario actualizado
    return user

# Eliminar usuario
@user_router.delete("/me", description="Eliminar el usuario actual")
def delete_user(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Cambiar estado de is_active True/False.
    """
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado",
        )
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    # Guardar los cambios
    db.commit()
    db.refresh(user)
    #return {"message": "Usuario eliminado"}
    return user