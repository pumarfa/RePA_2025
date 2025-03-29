from sqlalchemy import Column, String, Date, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.database import Base

class Training(Base):
    __tablename__ = "trainings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_curso = Column(String, nullable=False)
    institucion = Column(String, nullable=False)
    tipo_certificado = Column(String, nullable=False)
    nivel_estudio = Column(String, nullable=False)
    fecha_inicio = Column(Date)
    fecha_finalizacion = Column(Date)
    horas_duracion = Column(Integer, nullable=False)
    enlace_certificado = Column(String)
    area_conocimiento = Column(String, nullable=False)
    descripcion_curso = Column(String)
    calificacion_nota = Column(String)
    idioma = Column(String)
    nombre_profesor_instructor = Column(String)
    nombre_programa_estudios = Column(String)
    pais = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    estado_provincia = Column(String)
    observaciones = Column(String)

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="trainings") # Relación uno a muchos con usuario
    

