from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.services.finanza_service import FinanzaService
from app.services.deps import solo_barbero
from datetime import datetime, timedelta

router    = APIRouter(tags=["finanzas"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/barbero/finanzas", response_class=HTMLResponse)
def finanzas_page(request: Request, db: Session = Depends(get_db),
                  usuario: Usuario = Depends(solo_barbero)):
    movimientos = FinanzaService.obtener_movimientos(db)
    return templates.TemplateResponse(request, "barbero/finanzas.html",
                                      {"usuario": usuario, "movimientos": movimientos})

@router.post("/barbero/finanzas")
def registrar_movimiento(request: Request, db: Session = Depends(get_db),
                         usuario: Usuario = Depends(solo_barbero),
                         tipo:        str   = Form(...),
                         descripcion: str   = Form(...),
                         monto:       float = Form(...)):
    try:
        FinanzaService.registrar_movimiento(db, tipo, descripcion, monto)
        movimientos = FinanzaService.obtener_movimientos(db)
        return templates.TemplateResponse(request, "barbero/finanzas.html", {
            "usuario": usuario, "movimientos": movimientos,
            "mensaje": "✅ Movimiento registrado correctamente"
        })
    except ValueError as e:
        movimientos = FinanzaService.obtener_movimientos(db)
        return templates.TemplateResponse(request, "barbero/finanzas.html", {
            "usuario": usuario, "movimientos": movimientos,
            "error": str(e)
        })



@router.get("/barbero/reporte", response_class=HTMLResponse)
def reporte_semanal(request: Request, db: Session = Depends(get_db),
                    usuario: Usuario = Depends(solo_barbero),
                    fecha: str = None):
    reporte = FinanzaService.reporte_semanal(db, fecha_referencia=fecha)

    # Calcular fechas para navegación
    inicio_dt      = datetime.strptime(reporte["semana_inicio"], "%Y-%m-%d")
    fecha_anterior = (inicio_dt - timedelta(days=7)).strftime("%Y-%m-%d")
    fecha_siguiente = (inicio_dt + timedelta(days=7)).strftime("%Y-%m-%d")

    # No permitir ir más allá de la semana actual
    hoy             = datetime.today()
    inicio_actual   = hoy - timedelta(days=hoy.weekday())
    es_semana_actual = inicio_dt.date() >= inicio_actual.date()

    return templates.TemplateResponse(request, "barbero/reporte.html", {
        "usuario":        usuario,
        "reporte":        reporte,
        "fecha_anterior": fecha_anterior,
        "fecha_siguiente": fecha_siguiente,
        "es_semana_actual": es_semana_actual
    })