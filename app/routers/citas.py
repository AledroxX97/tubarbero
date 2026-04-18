from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.models.cita import Cita, EstadoCita
from app.models.servicio import Servicio
from app.services.cita_service import CitaService
from app.services.deps import get_current_user, solo_cliente, solo_barbero
from app.models.usuario import HorarioBarbero

router     = APIRouter(tags=["citas"])
templates  = Jinja2Templates(directory="app/templates")



@router.get("/cliente/dashboard", response_class=HTMLResponse)
def dashboard_cliente(request: Request, db: Session = Depends(get_db),
                      usuario: Usuario = Depends(solo_cliente)):
    citas = db.query(Cita).filter(Cita.cliente_id == usuario.id)\
               .order_by(Cita.fecha_hora.desc()).all()
    return templates.TemplateResponse(request, "cliente/dashboard.html",
                                      {"usuario": usuario, "citas": citas})

@router.get("/barbero/dashboard", response_class=HTMLResponse)
def dashboard_barbero(request: Request, db: Session = Depends(get_db),
                      usuario: Usuario = Depends(solo_barbero)):
    hoy   = date.today()
    citas = db.query(Cita).filter(Cita.barbero_id == usuario.id)\
               .order_by(Cita.fecha_hora).all()
    citas_hoy         = [c for c in citas if c.fecha_hora.date() == hoy]
    citas_confirmadas = sum(1 for c in citas_hoy if c.estado == EstadoCita.confirmada)
    citas_pendientes  = sum(1 for c in citas_hoy if c.estado == EstadoCita.pendiente)
    return templates.TemplateResponse(request, "barbero/dashboard.html", {
        "usuario": usuario, "citas": citas,
        "citas_hoy": citas_hoy,
        "citas_confirmadas": citas_confirmadas,
        "citas_pendientes": citas_pendientes
    })



@router.get("/citas/nueva", response_class=HTMLResponse)
def nueva_cita_page(request: Request, db: Session = Depends(get_db),
                    usuario: Usuario = Depends(solo_cliente)):
    barberos  = db.query(Usuario).filter(Usuario.rol == RolUsuario.barbero).all()
    servicios = db.query(Servicio).all()
    fecha_min = date.today().isoformat()
    return templates.TemplateResponse(request, "citas/nueva.html", {
        "usuario": usuario, "barberos": barberos,
        "servicios": servicios, "fecha_min": fecha_min
    })

@router.post("/citas/nueva")
def nueva_cita(request: Request, db: Session = Depends(get_db),
               usuario: Usuario = Depends(solo_cliente),
               barbero_id:  int = Form(...),
               servicio_id: int = Form(...),
               fecha:       str = Form(...),
               hora:        str = Form(...),
               notas:       str = Form("")):
    try:
        CitaService.crear_cita(db, usuario.id, barbero_id, servicio_id, fecha, hora, notas)
        return RedirectResponse(url="/cliente/dashboard", status_code=302)
    except ValueError as e:
        barberos  = db.query(Usuario).filter(Usuario.rol == RolUsuario.barbero).all()
        servicios = db.query(Servicio).all()
        return templates.TemplateResponse(request, "citas/nueva.html", {
            "usuario": usuario, "error": str(e),
            "barberos": barberos, "servicios": servicios,
            "fecha_min": date.today().isoformat()
        })
    


@router.get("/citas/horarios")
def horarios_disponibles(barbero_id: int, fecha: str, db: Session = Depends(get_db)):
    horarios = CitaService.obtener_horarios_disponibles(db, barbero_id, fecha)
    return {"horarios": horarios}




@router.get("/citas/servicios")
def servicios_por_barbero(barbero_id: int, db: Session = Depends(get_db)):
    servicios = db.query(Servicio).filter(Servicio.barbero_id == barbero_id).all()
    return {"servicios": [{"id": s.id, "nombre": s.nombre,
                           "precio": s.precio, "duracion": s.duracion} for s in servicios]}



@router.get("/citas/{cita_id}/cancelar")
def cancelar(cita_id: int, db: Session = Depends(get_db),
             usuario: Usuario = Depends(get_current_user)):
    try:
        CitaService.cancelar_cita(db, cita_id, usuario.id)
    except ValueError:
        pass
    destino = "/barbero/dashboard" if usuario.rol == "barbero" else "/cliente/dashboard"
    return RedirectResponse(url=destino, status_code=302)



@router.get("/citas/{cita_id}/reprogramar", response_class=HTMLResponse)
def reprogramar_page(cita_id: int, request: Request, db: Session = Depends(get_db),
                     usuario: Usuario = Depends(solo_cliente)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    return templates.TemplateResponse(request, "citas/reprogramar.html", {
        "usuario": usuario, "cita": cita,
        "fecha_min": date.today().isoformat()
    })

@router.post("/citas/{cita_id}/reprogramar")
def reprogramar(cita_id: int, db: Session = Depends(get_db),
                usuario: Usuario = Depends(solo_cliente),
                fecha: str = Form(...), hora: str = Form(...)):
    try:
        CitaService.reprogramar_cita(db, cita_id, usuario.id, fecha, hora)
        return RedirectResponse(url="/cliente/dashboard", status_code=302)
    except ValueError as e:
        cita = db.query(Cita).filter(Cita.id == cita_id).first()
        return RedirectResponse(url=f"/citas/{cita_id}/reprogramar", status_code=302)



@router.get("/citas/{cita_id}/confirmar")
def confirmar(cita_id: int, db: Session = Depends(get_db),
              usuario: Usuario = Depends(solo_barbero)):
    CitaService.confirmar_cita(db, cita_id)
    return RedirectResponse(url="/barbero/dashboard", status_code=302)

@router.get("/citas/{cita_id}/completar")
def completar(cita_id: int, db: Session = Depends(get_db),
              usuario: Usuario = Depends(solo_barbero)):
    CitaService.completar_cita(db, cita_id)
    return RedirectResponse(url="/barbero/dashboard", status_code=302)



@router.get("/barbero/horario", response_class=HTMLResponse)
def horario_page(request: Request, db: Session = Depends(get_db),
                 usuario: Usuario = Depends(solo_barbero)):
    horario = db.query(HorarioBarbero).filter(
        HorarioBarbero.barbero_id == usuario.id
    ).first()
    return templates.TemplateResponse(request, "barbero/horario.html",
                                      {"usuario": usuario, "horario": horario})

@router.post("/barbero/horario")
def guardar_horario(request: Request, db: Session = Depends(get_db),
                    usuario: Usuario = Depends(solo_barbero),
                    hora_inicio: str = Form(...),
                    hora_fin:    str = Form(...),
                    activo:      str = Form(None)):

    
    if hora_inicio >= hora_fin:
        horario = db.query(HorarioBarbero).filter(
            HorarioBarbero.barbero_id == usuario.id).first()
        return templates.TemplateResponse(request, "barbero/horario.html", {
            "usuario": usuario, "horario": horario,
            "error": "La hora de apertura debe ser menor que la de cierre"
        })

    horario = db.query(HorarioBarbero).filter(
        HorarioBarbero.barbero_id == usuario.id).first()

    if horario:
        horario.hora_inicio = hora_inicio
        horario.hora_fin    = hora_fin
        horario.activo      = activo == "on"
    else:
        horario = HorarioBarbero(
            barbero_id  = usuario.id,
            hora_inicio = hora_inicio,
            hora_fin    = hora_fin,
            activo      = activo == "on"
        )
        db.add(horario)

    db.commit()

    horario = db.query(HorarioBarbero).filter(
        HorarioBarbero.barbero_id == usuario.id).first()
    return templates.TemplateResponse(request, "barbero/horario.html", {
        "usuario": usuario, "horario": horario,
        "mensaje": "✅ Horario guardado correctamente"
    })



@router.get("/barbero/servicios", response_class=HTMLResponse)
def servicios_page(request: Request, db: Session = Depends(get_db),
                   usuario: Usuario = Depends(solo_barbero)):
    servicios = db.query(Servicio).filter(Servicio.barbero_id == usuario.id).all()
    return templates.TemplateResponse(request, "barbero/servicios.html",
                                      {"usuario": usuario, "servicios": servicios, "editar": None})

@router.post("/barbero/servicios")
def crear_servicio(request: Request, db: Session = Depends(get_db),
                   usuario: Usuario = Depends(solo_barbero),
                   nombre:   str   = Form(...),
                   precio:   float = Form(...),
                   duracion: int   = Form(...)):
    try:
        servicio = Servicio(barbero_id=usuario.id, nombre=nombre,
                            precio=precio, duracion=duracion)
        db.add(servicio)
        db.commit()
        servicios = db.query(Servicio).filter(Servicio.barbero_id == usuario.id).all()
        return templates.TemplateResponse(request, "barbero/servicios.html", {
            "usuario": usuario, "servicios": servicios, "editar": None,
            "mensaje": "✅ Servicio creado correctamente"
        })
    except Exception as e:
        servicios = db.query(Servicio).filter(Servicio.barbero_id == usuario.id).all()
        return templates.TemplateResponse(request, "barbero/servicios.html", {
            "usuario": usuario, "servicios": servicios, "editar": None,
            "error": str(e)
        })

@router.get("/barbero/servicios/{servicio_id}/editar", response_class=HTMLResponse)
def editar_servicio_page(servicio_id: int, request: Request, db: Session = Depends(get_db),
                         usuario: Usuario = Depends(solo_barbero)):
    servicio  = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    servicios = db.query(Servicio).filter(Servicio.barbero_id == usuario.id).all()
    return templates.TemplateResponse(request, "barbero/servicios.html",
                                      {"usuario": usuario, "servicios": servicios, "editar": servicio})

@router.post("/barbero/servicios/{servicio_id}/editar")
def editar_servicio(servicio_id: int, request: Request, db: Session = Depends(get_db),
                    usuario: Usuario = Depends(solo_barbero),
                    nombre:   str   = Form(...),
                    precio:   float = Form(...),
                    duracion: int   = Form(...)):
    servicio          = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    servicio.nombre   = nombre
    servicio.precio   = precio
    servicio.duracion = duracion
    db.commit()
    return RedirectResponse(url="/barbero/servicios", status_code=302)

@router.get("/barbero/servicios/{servicio_id}/eliminar")
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db),
                      usuario: Usuario = Depends(solo_barbero)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if servicio:
        db.delete(servicio)
        db.commit()
    return RedirectResponse(url="/barbero/servicios", status_code=302)