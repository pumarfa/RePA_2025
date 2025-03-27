from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # Para el debug de errores
from typing import List

from src.models.training_models import Training
from src.schemas.trainig_schemas import TrainingOut

from src.database import get_db
from src.utils import get_current_user, has_user_role

admin_training = APIRouter()

@admin_training.get("/training", response_model=List[TrainingOut], description="Obtener todos los cursos")
async def get_training(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Obtener todos los cursos (Sólo para Administradores).
    Args:
        db (Session): Sesión de la base de datos proporcionada por la dependencia.
        current_user (dict): Usuario actual proporcionado por la dependencia.

    Returns:
        List[Training]: Lista de todos los cursos disponibles.

    Raises:
        HTTPException: Si el usuario no tiene permisos de administrador.
    """
    print(f"Admin Training - get_training - current_user: {current_user}") # Debug
    # Verificar si el usuario tiene el rol "admin"
    if not has_user_role(current_user, ["admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )
    training = db.query(Training).all()
    return training
    