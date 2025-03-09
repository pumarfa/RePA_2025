from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.user_model import User, UserRole, Role
from src.auth.auth import get_current_user

def has_role(required_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> bool:
        # Verifica si el usuario tiene al menos un rol en la lista de roles requeridos
        return any(role.rol in required_roles for role in current_user.roles)
    return role_checker

# Verifica si el usuario tiene al menos uno de los roles requeridos
def has_user_role(user: User, required_roles: list[str]) -> bool:
    """
    Retorna True si el usuario posee al menos uno de los roles requeridos,
    False en caso contrario.
    """
    return any(role.rol in required_roles for role in user.roles)

