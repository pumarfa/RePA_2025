from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # PAra el debug de errores
from src.db.seed import seed_data # Se mueve la función 'seed_data' a la libreria de 'seed' sólamente para la instalación de roles iniciales.
from src.models.user_model import User
from src.schemas.user_schema import UserCreate, UserOut, RoleOut
from src.db.database import get_db
from datetime import datetime

seed_router = APIRouter()

# Ruta protegida de ejemplo
@seed_router.post("/seed", response_model=RoleOut)
def seed_init_data(db: Session = Depends(get_db)):
    seed_init_data = seed_data()
    return seed_init_data
