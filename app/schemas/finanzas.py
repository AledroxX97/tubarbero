from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class TipoMovimiento(str, Enum):
    ingreso = "ingreso"
    gasto   = "gasto"

class MovimientoCreate(BaseModel):
    tipo:        TipoMovimiento
    descripcion: str
    monto:       float

class MovimientoOut(BaseModel):
    id:          int
    tipo:        TipoMovimiento
    descripcion: str
    monto:       float
    fecha:       datetime

    class Config:
        from_attributes = True