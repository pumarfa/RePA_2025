from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # PAra el debug de errores
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from src.auth.auth import create_access_token, verify_token, get_current_user # Se mueve la funcion 'get_current_user' a la libreria de 'auth'
from src.auth.permissions import has_role, has_user_role
from src.models.user_model import User
from src.schemas.user_schema import UserCreate, UserOut, UserUpdate
from src.db.database import get_db
from datetime import datetime

admin_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Obtener un usuario por user_id
@admin_router.get("/{user_id}", response_model=UserOut, description="Obtener un usuario por user_id")
def get_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Obtener un usuario por user_id.
    """
    if not has_user_role(current_user, ['admin']):
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este usuario")
    
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

# Listar todos los usuarios, solo para los administradores
@admin_router.get("/users", response_model=list[UserOut], description="Listar todos los usuarios, solo para los administradores")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(has_role(["admin"]))):
    """
    Listar todos los usuarios.
    """
    # Solo los administradores pueden ver la lista completa
    if not has_user_role(current_user, ['admin']):
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este usuario")
    
    return db.query(User).all()

# Modificar un usuario por user_id, solo para administrador
@admin_router.put("/{user_id}", response_model=UserOut, description="Modificar un usuario por user_id, solo para administrador")
def update_user(user_id: str, user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Modificar un usuario por user_id.
    """
    if not has_user_role(current_user, ['admin']):
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este usuario")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.email = user_in.email
    db_user.hashed_password = pwd_context.hash(user_in.password)
    db.commit()
    db.refresh(db_user)
    return db_user

# Eliminar un usuario por user_id, solo para administrador
@admin_router.delete("/{user_id}", description="Eliminar un usuario por user_id, solo para administrador. Set is_active=False")
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Elimina un usuario por user_id.
    Se establece el campo is_active en False.
    """
    if not has_user_role(current_user, ['admin']):
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este usuario")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user

# Gestionar roles de un usuario
@admin_router.post("/{user_id}/roles", description="Gestionar roles de un usuario")
def manage_user_roles(user_id: str, roles: list[str], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gestionar roles de un usuario.
    """
    if not has_user_role(current_user, ['admin']):
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este usuario")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.roles = roles
    db.commit()
    db.refresh(db_user)
    return db_user