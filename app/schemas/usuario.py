from pydantic import BaseModel, EmailStr
from enum import Enum

class RolUsuario(str, Enum):
    cliente = "cliente"
    barbero = "barbero"

# Para registrarse
class UsuarioCreate(BaseModel):
    nombre:   str
    email:    EmailStr
    telefono: str
    password: str
    rol:      RolUsuario

# Para mostrar datos (nunca expone el password)
class UsuarioOut(BaseModel):
    id:     int
    nombre: str
    email:  str
    rol:    RolUsuario

    class Config:
        from_attributes = True

# Para login
class LoginData(BaseModel):
    email:    EmailStr
    password: str

# Token JWT que se devuelve al cliente
class Token(BaseModel):
    access_token: str
    token_type:   str
    rol:          str
    nombre:       str