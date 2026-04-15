from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Servicio(Base):
    __tablename__ = "servicios"

    id         = Column(Integer, primary_key=True, index=True)
    barbero_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre     = Column(String(100), nullable=False)
    precio     = Column(Float, nullable=False)
    duracion   = Column(Integer, nullable=False)  # en minutos

    barbero = relationship("Usuario")