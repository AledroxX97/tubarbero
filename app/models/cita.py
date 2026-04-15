from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class EstadoCita(str, enum.Enum):
    pendiente   = "pendiente"
    confirmada  = "confirmada"
    cancelada   = "cancelada"
    completada  = "completada"

class Cita(Base):
    __tablename__ = "citas"

    id          = Column(Integer, primary_key=True, index=True)
    cliente_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    barbero_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    fecha_hora  = Column(DateTime, nullable=False)
    estado      = Column(Enum(EstadoCita), default=EstadoCita.pendiente)
    notas       = Column(String(300))

    cliente  = relationship("Usuario", foreign_keys=[cliente_id])
    barbero  = relationship("Usuario", foreign_keys=[barbero_id])
    servicio = relationship("Servicio")