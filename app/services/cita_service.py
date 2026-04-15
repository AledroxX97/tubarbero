from sqlalchemy.orm import Session
from app.models.cita import Cita, EstadoCita
from app.models.usuario import Usuario
from app.models.servicio import Servicio
from datetime import datetime, timedelta
from app.models.usuario import HorarioBarbero
from app.models.finanzas import Movimiento, TipoMovimiento

HORA_INICIO = 8   # 8:00 AM
HORA_FIN    = 18  # 6:00 PM

class CitaService:

    @staticmethod
    def obtener_horarios_disponibles(db: Session, barbero_id: int, fecha: str) -> list:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")

        if fecha_dt.date() < datetime.today().date():
            return []

        # Obtener horario del barbero
        horario = db.query(HorarioBarbero).filter(
         HorarioBarbero.barbero_id == barbero_id
        ).first()

        if horario and not horario.activo:
            return []

        if horario:
            h_ini, m_ini = map(int, horario.hora_inicio.split(":"))
            h_fin, m_fin = map(int, horario.hora_fin.split(":"))
        else:
            h_ini, m_ini = HORA_INICIO, 0
            h_fin, m_fin = HORA_FIN, 0

        # Citas ocupadas — incluir completadas para bloquear esa hora igual
        citas_del_dia = db.query(Cita).filter(
            Cita.barbero_id == barbero_id,
            Cita.estado.in_(["pendiente", "confirmada", "completada"]),  # ← aquí el cambio
            Cita.fecha_hora >= fecha_dt,
            Cita.fecha_hora < fecha_dt + timedelta(days=1)
        ).all()

        rangos_bloqueados = []
        for c in citas_del_dia:
            inicio   = c.fecha_hora
            duracion = c.servicio.duracion if c.servicio else 30
            fin      = inicio + timedelta(minutes=duracion)
            rangos_bloqueados.append((inicio, fin))

        horarios    = []
        hora_actual = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, h_ini, m_ini)
        hora_limite = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, h_fin, m_fin)

        # Si es hoy, no mostrar horas pasadas
        ahora = datetime.now()
        if fecha_dt.date() == ahora.date():
            # Avanzar al próximo slot futuro
            while hora_actual <= ahora:
                hora_actual += timedelta(minutes=30)

        while hora_actual < hora_limite:
            bloqueado = any(inicio <= hora_actual < fin for inicio, fin in rangos_bloqueados)
            if not bloqueado:
                horarios.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(minutes=30)

        return horarios  

    @staticmethod
    def crear_cita(db: Session, cliente_id: int, barbero_id: int,
                   servicio_id: int, fecha: str, hora: str, notas: str = "") -> Cita:
        fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")

        disponibles = CitaService.obtener_horarios_disponibles(db, barbero_id, fecha)
        if hora not in disponibles:
            raise ValueError("El horario seleccionado ya no está disponible")

        cita = Cita(
            cliente_id  = cliente_id,
            barbero_id  = barbero_id,
            servicio_id = servicio_id,
            fecha_hora  = fecha_hora,
            estado      = EstadoCita.pendiente,
            notas       = notas
        )
        db.add(cita)
        db.commit()
        db.refresh(cita)
        return cita

    @staticmethod
    def cancelar_cita(db: Session, cita_id: int, usuario_id: int) -> Cita:
        cita = db.query(Cita).filter(Cita.id == cita_id).first()
        if not cita:
            raise ValueError("Cita no encontrada")
        if cita.cliente_id != usuario_id and cita.barbero_id != usuario_id:
            raise ValueError("No tienes permiso para cancelar esta cita")
        cita.estado = EstadoCita.cancelada
        db.commit()
        return cita

    @staticmethod
    def reprogramar_cita(db: Session, cita_id: int, cliente_id: int,
                         fecha: str, hora: str) -> Cita:
        cita = db.query(Cita).filter(Cita.id == cita_id).first()
        if not cita:
            raise ValueError("Cita no encontrada")
        if cita.cliente_id != cliente_id:
            raise ValueError("No tienes permiso")

        disponibles = CitaService.obtener_horarios_disponibles(db, cita.barbero_id, fecha)
        if hora not in disponibles:
            raise ValueError("El horario seleccionado no está disponible")

        cita.fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        cita.estado     = EstadoCita.pendiente
        db.commit()
        return cita

    @staticmethod
    def confirmar_cita(db: Session, cita_id: int) -> Cita:
        cita = db.query(Cita).filter(Cita.id == cita_id).first()
        if not cita:
            raise ValueError("Cita no encontrada")
        cita.estado = EstadoCita.confirmada
        db.commit()
        return cita

    @staticmethod
    def completar_cita(db: Session, cita_id: int) -> Cita:
        cita = db.query(Cita).filter(Cita.id == cita_id).first()
        if not cita:
            raise ValueError("Cita no encontrada")
    
        cita.estado = EstadoCita.completada
    
        # Registrar ingreso automáticamente
        ingreso = Movimiento(
            tipo        = TipoMovimiento.ingreso,
            descripcion = f"Servicio: {cita.servicio.nombre} — Cliente: {cita.cliente.nombre}",
            monto       = cita.servicio.precio,
            cita_id     = cita_id
        )
        db.add(ingreso)
        db.commit()
        return cita