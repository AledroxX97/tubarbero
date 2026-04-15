from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.usuario import UsuarioCreate

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"usuario": None})

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        usuario = AuthService.login(db, email, password)
        token   = AuthService.crear_token({"id": usuario.id, "rol": usuario.rol})
        destino = "/barbero/dashboard" if usuario.rol == "barbero" else "/cliente/dashboard"
        response = RedirectResponse(url=destino, status_code=302)
        response.set_cookie("access_token", token, httponly=True)
        return response
    except ValueError as e:
        return templates.TemplateResponse(request, "login.html", {"error": str(e), "usuario": None})

@router.get("/registro", response_class=HTMLResponse)
def registro_page(request: Request):
    return templates.TemplateResponse(request, "registro.html", {"usuario": None})

@router.post("/registro")
def registro(
    request: Request,
    nombre:   str = Form(...),
    email:    str = Form(...),
    telefono: str = Form(...),
    password: str = Form(...),
    rol:      str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        datos = UsuarioCreate(nombre=nombre, email=email, telefono=telefono, password=password, rol=rol)
        AuthService.registrar_usuario(db, datos)
        return RedirectResponse(url="/auth/login", status_code=302)
    except ValueError as e:
        return templates.TemplateResponse(request, "registro.html", {"error": str(e), "usuario": None})

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response