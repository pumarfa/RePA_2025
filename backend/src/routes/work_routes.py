from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.work_models import Work, RolWork, TareaWork
from src.schemas.work_schemas import TrabajoCreate, Trabajo, RolAtWork, TareaAtWork
from src.logger import logger
from src.utils import get_current_user
from src.models.user_models import User
from typing import List

# Crear el router para las rutas de trabajo
work_router = APIRouter()

# Obtener todos los trabajos
@work_router.get("/", response_model=List[Trabajo],description="Obtener todos los trabajos del usuario")
def get_trabajos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar si el usuario está autenticado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Obtener todos los trabajos del usuario
    trabajos = db.query(Work).filter(Work.user_id == current_user["id"]).all()
    
    if not trabajos:
        raise HTTPException(status_code=404, detail="No se encontraron trabajos")
    
    return trabajos

# Crear un nuevo trabajo
@work_router.post("/", response_model=Trabajo, description="Crear un nuevo trabajo")
def create_trabajo(
    trabajo: TrabajoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar si el usuario está autenticado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado")
    # print(f'work routes - create_trabajo - Datos completos de entrada {trabajo}')
    # print(f'work routes - create_trabajo - Usuario Registrado: {current_user["id"]}')
    # Crear el nuevo trabajo
    db_trabajo = Work(
        titulo_produccion=trabajo.titulo_produccion,
        tipo_produccion=trabajo.tipo_produccion,
        fecha_inicio=trabajo.fecha_inicio,
        fecha_fin=trabajo.fecha_fin,
        descripcion=trabajo.descripcion,
        enlace_portafolio=trabajo.enlace_portafolio,
        user_id=current_user["id"]
    )
    
    # Agregar roles y tareas al trabajo(Pasar a minusculas) 
    for rol in trabajo.roles:
        db_rol = db.query(RolWork).filter(RolWork.nombre == rol.nombre).first()
        if not db_rol:
            db_rol = RolWork(nombre=rol.nombre)
            db.add(db_rol)
            db.commit()
            db.refresh(db_rol)
        db_trabajo.roles.append(db_rol)
    
    for tarea in trabajo.tareas:
        db_tarea = db.query(TareaWork).filter(TareaWork.nombre == tarea.nombre).first()
        if not db_tarea:
            db_tarea = TareaWork(nombre=tarea.nombre)
            db.add(db_tarea)
            db.commit()
            db.refresh(db_tarea)
        db_trabajo.tareas.append(db_tarea)
    
    # Guardar el trabajo en la base de datos
    db.add(db_trabajo)
    db.commit()
    db.refresh(db_trabajo)
    
    logger.info(f"Trabajo creado con éxito: {db_trabajo.id}")
    
    return db_trabajo

# Obtener un trabajo por ID
@work_router.get("/{trabajo_id}", response_model=Trabajo, description="Obtener un trabajo por ID")
def get_trabajo(
    trabajo_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar si el usuario está autenticado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Obtener el trabajo por ID
    trabajo = db.query(Work).filter(Work.id == trabajo_id, Work.user_id == current_user["id"]).first()
    
    if not trabajo:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    return trabajo

# Actualizar un trabajo por ID
@work_router.put("/{trabajo_id}", response_model=Trabajo, description="Actualizar un trabajo por ID")
def update_trabajo(
    trabajo_id: int,
    trabajo: TrabajoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar si el usuario está autenticado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Obtener el trabajo por ID
    db_trabajo = db.query(Work).filter(Work.id == trabajo_id, Work.user_id == current_user["id"]).first()
    
    if not db_trabajo:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    # Actualizar los campos del trabajo
    db_trabajo.titulo_produccion = trabajo.titulo_produccion
    db_trabajo.tipo_produccion = trabajo.tipo_produccion
    db_trabajo.fecha_inicio = trabajo.fecha_inicio
    db_trabajo.fecha_fin = trabajo.fecha_fin
    db_trabajo.descripcion = trabajo.descripcion
    db_trabajo.enlace_portafolio = trabajo.enlace_portafolio
    
    # Limpiar roles y tareas existentes
    db_trabajo.roles.clear()
    db_trabajo.tareas.clear()
    
    # Agregar roles y tareas al trabajo
    for rol in trabajo.roles:
        db_rol = db.query(RolAtWork).filter(RolAtWork.nombre == rol.nombre).first()
        if not db_rol:
            db_rol = RolAtWork(nombre=rol.nombre)
            db.add(db_rol)
            db.commit()
            db.refresh(db_rol)
        db_trabajo.roles.append(db_rol)
    
    for tarea in trabajo.tareas:
        db_tarea = db.query(TareaAtWork).filter(TareaAtWork.nombre == tarea.nombre).first()
        if not db_tarea:
            db_tarea = TareaAtWork(nombre=tarea.nombre)
            db.add(db_tarea)
            db.commit()
            db.refresh(db_tarea)
        db_trabajo.tareas.append(db_tarea)
    
    # Guardar los cambios en la base de datos
    db.commit()
    
    logger.info(f"Trabajo actualizado con éxito: {db_trabajo.id}")
    
    return db_trabajo

# Eliminar un trabajo por ID
@work_router.delete("/{trabajo_id}", response_model=Trabajo, description="Eliminar un trabajo por ID")
def delete_trabajo(
    trabajo_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar si el usuario está autenticado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Obtener el trabajo por ID
    db_trabajo = db.query(Work).filter(Work.id == trabajo_id, Work.user_id == current_user["id"]).first()
    
    if not db_trabajo:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    # Eliminar el trabajo de la base de datos
    db.delete(db_trabajo)
    db.commit()
    
    logger.info(f"Trabajo eliminado con éxito: {db_trabajo.id}")
    
    return db_trabajo

# Obtener todos los roles
@work_router.get("/roles", response_model=List[RolAtWork], description="Obtener todos los roles")
def get_roles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar si el usuario está autenticado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Obtener todos los roles
    roles = db.query(RolAtWork).all()
    
    if not roles:
        raise HTTPException(status_code=404, detail="No se encontraron roles")
    
    return roles

# Obtener todas las tareas
@work_router.get("/tareas", response_model=List[TareaAtWork], description="Obtener todas las tareas")
def get_tareas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar si el usuario está autenticado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    # Obtener todas las tareas
    tareas = db.query(TareaAtWork).all()
    
    if not tareas:
        raise HTTPException(status_code=404, detail="No se encontraron tareas")
    
    return tareas

