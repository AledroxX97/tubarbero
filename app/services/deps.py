from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.services.auth_service import AuthService

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Usuario:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    payload = AuthService.verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == payload.get("id")).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return usuario

def solo_barbero(usuario: Usuario = Depends(get_current_user)):
    if usuario.rol != "barbero":
        raise HTTPException(status_code=403, detail="Acceso solo para barberos")
    return usuario

def solo_cliente(usuario: Usuario = Depends(get_current_user)):
    if usuario.rol != "cliente":
        raise HTTPException(status_code=403, detail="Acceso solo para clientes")
    return usuario