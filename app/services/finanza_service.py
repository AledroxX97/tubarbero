from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.finanzas import Movimiento, TipoMovimiento
from app.models.cita import Cita, EstadoCita
from datetime import datetime, timedelta

class FinanzaService:

    @staticmethod
    def registrar_movimiento(db: Session, tipo: str, descripcion: str,
                             monto: float, cita_id: int = None) -> Movimiento:
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        movimiento = Movimiento(
            tipo        = tipo,
            descripcion = descripcion,
            monto       = monto,
            cita_id     = cita_id
        )
        db.add(movimiento)
        db.commit()
        db.refresh(movimiento)
        return movimiento

    @staticmethod
    def obtener_movimientos(db: Session, tipo: str = None) -> list:
        query = db.query(Movimiento)
        if tipo:
            query = query.filter(Movimiento.tipo == tipo)
        return query.order_by(Movimiento.fecha.desc()).all()
 
    
    @staticmethod
    def reporte_semanal(db: Session, fecha_referencia: str = None) -> dict:
        if fecha_referencia:
            hoy = datetime.strptime(fecha_referencia, "%Y-%m-%d")
        else:
            hoy = datetime.today()

        inicio = hoy - timedelta(days=hoy.weekday())  # lunes
        inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fin    = inicio + timedelta(days=7)

        movimientos = db.query(Movimiento).filter(
            Movimiento.fecha >= inicio,
            Movimiento.fecha <  fin
        ).all()

        ingresos = [m for m in movimientos if m.tipo == TipoMovimiento.ingreso]
        gastos   = [m for m in movimientos if m.tipo == TipoMovimiento.gasto]

        total_ingresos = sum(m.monto for m in ingresos)
        total_gastos   = sum(m.monto for m in gastos)

        dias = {}
        for i in range(7):
            dia = (inicio + timedelta(days=i)).strftime("%a %d/%m")
            dias[dia] = {"ingresos": 0, "gastos": 0}

        for m in movimientos:
            dia = m.fecha.strftime("%a %d/%m")
            if dia in dias:
                if m.tipo == TipoMovimiento.ingreso:
                    dias[dia]["ingresos"] += m.monto
                else:
                    dias[dia]["gastos"]   += m.monto

        return {
            "ingresos":       total_ingresos,
            "gastos":         total_gastos,
            "balance":        total_ingresos - total_gastos,
            "detalle_dias":   dias,
            "lista_ingresos": ingresos,
            "lista_gastos":   gastos,
            "semana_inicio":  inicio.strftime("%Y-%m-%d"),
            "semana_fin":     (fin - timedelta(days=1)).strftime("%d/%m/%Y"),
            "semana_inicio_display": inicio.strftime("%d/%m/%Y"),
        }
    