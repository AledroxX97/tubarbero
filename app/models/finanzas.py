from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from app.database import Base
from datetime import datetime
import enum

class TipoMovimiento(str, enum.Enum):
    ingreso = "ingreso"
    gasto   = "gasto"

class Movimiento(Base):
    __tablename__ = "movimientos"

    id          = Column(Integer, primary_key=True, index=True)
    tipo        = Column(Enum(TipoMovimiento), nullable=False)
    descripcion = Column(String(200))
    monto       = Column(Float, nullable=False)
    fecha       = Column(DateTime, default=datetime.utcnow)
    cita_id     = Column(Integer, ForeignKey("citas.id"), nullable=True)