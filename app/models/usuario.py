from sqlalchemy import Column, Integer, String, Boolean, Enum, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RolUsuario(str, enum.Enum):
    cliente = "cliente"
    barbero = "barbero"

class Usuario(Base):
    __tablename__ = "usuarios"

    id       = Column(Integer, primary_key=True, index=True)
    nombre   = Column(String(100), nullable=False)
    email    = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20))
    password = Column(String(255), nullable=False)  # siempre encriptada
    rol      = Column(Enum(RolUsuario), nullable=False)
    activo   = Column(Boolean, default=True)
    horario  = relationship("HorarioBarbero", back_populates="barbero", uselist=False)

class HorarioBarbero(Base):
    __tablename__ = "horarios_barbero"

    id           = Column(Integer, primary_key=True, index=True)
    barbero_id   = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    hora_inicio  = Column(String(5), default="08:00")  # formato "HH:MM"
    hora_fin     = Column(String(5), default="18:00")
    activo       = Column(Boolean, default=True)        # si atiende ese día o no

    barbero = relationship("Usuario", back_populates="horario")