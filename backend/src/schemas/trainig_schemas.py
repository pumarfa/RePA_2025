from pydantic import BaseModel, HttpUrl, constr
from typing import Optional
from datetime import datetime

class TrainingBase(BaseModel):
    nombre_curso: str
    institucion: str
    tipo_certificado: str
    nivel_estudio: str
    fecha_inicio: datetime
    fecha_finalizacion: datetime
    horas_duracion: float
    enlace_certificado: str ## Optional[HttpUrl]: None  # Puede ser None o URL
    area_conocimiento: str
    descripcion_curso: constr( max_length=1500)
    calificacion_nota: str
    idioma: str
    nombre_profesor_instructor: str
    nombre_programa_estudios: str
    pais: str
    ciudad: str
    estado_provincia: str
    observaciones: constr( max_length=1000)

class TrainingCreate(TrainingBase):
    pass

class TrainingUpdate(TrainingBase):
    pass

class TrainingOut(TrainingBase):
    id: int
    user_id: str
    
    class Config:
        from_attributes = True