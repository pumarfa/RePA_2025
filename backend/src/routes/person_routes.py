# routes/person_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.person_model import Person
from src.schemas.person_schema import PersonCreate, PersonOut
from src.auth.permissions import has_role
from src.models.user_model import User

person_router = APIRouter()

# Crear una nueva persona
@person_router.post("/", response_model=PersonOut)
def create_person(person: PersonCreate, db: Session = Depends(get_db), current_user: User = Depends(has_role(["admin", "editor"]))):
    db_person = db.query(Person).filter(Person.dni_cuit_cuil == person.dni_cuit_cuil).first()
    if db_person:
        raise HTTPException(status_code=400, detail="Persona con este DNI-CUIT-CUIL ya existe")
    if not current_user.email:
        raise HTTPException(status_code=400, detail="El usuario actual no tiene un correo asociado")

    new_person = Person(**person.dict(), user_email=current_user.email)
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person

# Obtener una persona por su ID
@person_router.get("/{person_id}", response_model=PersonOut)
def get_person(person_id: int, db: Session = Depends(get_db), current_user: User = Depends(has_role(["admin", "viewer"]))):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return person

# Actualizar datos de una persona
@person_router.put("/{person_id}", response_model=PersonOut)
def update_person(person_id: int, person: PersonCreate, db: Session = Depends(get_db), current_user: User = Depends(has_role(["admin", "editor"]))):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    for key, value in person.dict().items():
        setattr(db_person, key, value)
    db.commit()
    db.refresh(db_person)
    return db_person

# Eliminar una persona
@person_router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db), current_user: User = Depends(has_role(["admin"]))):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    db.delete(db_person)
    db.commit()
    return {"message": "Persona eliminada correctamente"}
