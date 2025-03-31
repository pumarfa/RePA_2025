from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from src.database import Base


# Tabla de asociación para la relación muchos a muchos entre Trabajos y Roles
trabajos_roles = Table('trabajos_roles', Base.metadata,
    Column('trabajo_id', Integer, ForeignKey('trabajos.id'), primary_key=True),
    Column('rol_id', Integer, ForeignKey('rol_at_work.id'), primary_key=True)
)

# Tabla de asociación para la relación muchos a muchos entre Trabajos y Tareas
trabajos_tareas = Table('trabajos_tareas', Base.metadata,
    Column('trabajo_id', Integer, ForeignKey('trabajos.id'), primary_key=True),
    Column('tarea_id', Integer, ForeignKey('tareas_at_work.id'), primary_key=True)
)

class Work(Base):
    __tablename__ = 'trabajos'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo_produccion = Column(String, nullable=False)
    tipo_produccion = Column(String)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    descripcion = Column(String)
    enlace_portafolio = Column(String)

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="trabajos") # Relación uno a muchos con usuario
    roles = relationship('RolWork', secondary=trabajos_roles, back_populates='trabajos')
    tareas = relationship('TareaWork', secondary=trabajos_tareas, back_populates='trabajos')

class RolWork(Base):
    __tablename__ = 'rol_at_work'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

    trabajos = relationship('Work', secondary=trabajos_roles, back_populates='roles')
    
class TareaWork(Base):
    __tablename__ = 'tareas_at_work'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

    trabajos = relationship('Work', secondary=trabajos_tareas, back_populates='tareas')
