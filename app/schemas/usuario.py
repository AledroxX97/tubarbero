from pydantic import BaseModel, EmailStr
from enum import Enum

class RolUsuario(str, Enum):
    cliente = "cliente"
    barbero = "barbero"


class UsuarioCreate(BaseModel):
    nombre:   str
    email:    EmailStr
    telefono: str
    password: str
    rol:      RolUsuario


class UsuarioOut(BaseModel):
    id:     int
    nombre: str
    email:  str
    rol:    RolUsuario

    class Config:
        from_attributes = True


class LoginData(BaseModel):
    email:    EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type:   str
    rol:          str
    nombre:       str