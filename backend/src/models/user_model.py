import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.db.database import Base
from datetime import datetime

# Tabla asociativa para la relación muchos a muchos entre usuarios y roles
class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

# Modelo de Role
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    rol = Column(String, unique=True, index=True, nullable=False)
    # Relación inversa definida en User

# Modelo de User
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=None, nullable=True)
    # Relación con roles a través de la tabla UserRole
    roles = relationship("Role", secondary="user_roles", backref="users")
    #person = relationship("Person", back_populates="user", uselist=False) # Relación 1:1 con Person
    #company = relationship("Company", back_populates="user", uselist=False) # Relación 1:N con Company
    #trainings = relationship("Training", back_populates="user")  # Relación 1:N con Training
    #audiovisual_works = relationship("AudiovisualWork", back_populates="user")  # Relación 1:N con AudiovisualWork
