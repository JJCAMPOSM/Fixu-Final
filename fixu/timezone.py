"""Conversión de fechas UTC (como se guardan en la BD) a la hora local de
la Ciudad de México para mostrarlas en la web. Todo lo que graba
datetime.utcnow() es naive-UTC; sin esta conversión los templates mostraban
la hora UTC cruda, adelantada 6 horas respecto a la hora real del usuario."""
from datetime import timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo('America/Mexico_City')


def to_local(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc).astimezone(LOCAL_TZ)


def format_local(dt, fmt='%Y-%m-%d %H:%M'):
    local = to_local(dt)
    return local.strftime(fmt) if local else ''
