from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import Base, engine
from app.models import usuario, cita, servicio, finanzas
from app.routers import auth, citas, finanzas as finanzas_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Barbería App")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(citas.router)
app.include_router(finanzas_router.router)


templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(request, "landing.html", {})