from app.database import SessionLocal, engine, Base

# Importar TODOS los modelos para que SQLAlchemy los registre
from app.models import usuario, cita, servicio, finanzas

# Crear las tablas
Base.metadata.create_all(bind=engine)

from app.models.servicio import Servicio

db = SessionLocal()

servicios = [
    Servicio(nombre="Corte clásico",       precio=15000, duracion=60),
    Servicio(nombre="Corte + barba",        precio=25000, duracion=80),
    Servicio(nombre="Barba", precio=12000, duracion=30),
    Servicio(nombre="Corte infantil",       precio=12000, duracion=50),
]

db.add_all(servicios)
db.commit()
db.close()
print("✅ Servicios creados correctamente")