from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # PAra el debug de errores
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from src.auth.auth import create_access_token, verify_token, get_current_user # Se mueve la funcion 'get_current_user' a la libreria de 'auth'
from src.auth.permissions import has_role
from src.models.user_model import User
from src.schemas.user_schema import UserCreate, UserOut, UserUpdate
from src.db.database import get_db
from datetime import datetime

user_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Actualizar último acceso... Esto se debe integrar a la ruta de logín del usuario.
# @user_router.patch("/{email}/last-login", response_model=UserOut)
def update_last_login(email: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    #return db_user

# Crear un usuario nuevo
@user_router.post("/register", response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    hashed_password = pwd_context.hash(user_in.password)

    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )
    # Asignar roles si se especifica (se espera que los roles existan)
    if user_in.roles:
        roles = db.query(Role).filter(Role.id.in_(user_in.roles)).all()
        new_user.roles = roles

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Inicio de sesión [form_data: OAuth2PasswordRequestForm = Depends()]
@user_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Actualizar el último login
    user.last_login =  datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# Actualizar usuario (por ejemplo, cambiar contraseña)
@user_router.put("/me", response_model=UserOut)
def update_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = pwd_context.hash(user_update.password)
    db.commit()
    db.refresh(current_user)
    return current_user

# Obtener un usuario por id
@user_router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Los administradores pueden acceder a cualquier usuario
    if has_user_role(user_id, '["admin"]') and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este usuario")
    
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

# Eliminar un usuario siempre el el email del current:user sea igual al del token
@user_router.delete("/{email}")
def delete_user(email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(db_user)
    db.commit()
    return {"message": "Usuario eliminado correctamente"}

# Listar todos los usuarios, solo para los administradores (ejemplo)
@user_router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(has_role(["admin"]))):
    # Solo los administradores pueden ver la lista completa
    return db.query(User).all()

# Ruta protegida de ejemplo
@user_router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
