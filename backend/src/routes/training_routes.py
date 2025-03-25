from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # PAra el debug de errores
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import List
from src.models.user_models import User
from src.models.training_models import Training
from src.schemas.trainig_schemas import TrainingBase, TrainingCreate, TrainingOut, TrainingUpdate
from src.database import get_db
from src.utils import get_current_user

training_router = APIRouter()

# Crear un Training
@training_router.put("/new", response_model=TrainingOut, status_code=status.HTTP_201_CREATED, description="Crear un nuevo curso")
async def create_training(training_in: TrainingCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Crear un curso nuevo para el usuairo
    """
    print(f"Current User is:{current_user}") # Debug
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado",
        )
    
    db_training = Training(**training_in.dict(), user_id=current_user["id"])
    db.add(db_training)
    db.commit()
    db.refresh(db_training)
    return db_training
    
