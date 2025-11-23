# Fixu — Mesa de Ayuda (Flask)

Aplicación Helpdesk Ticketing en Flask + Jinja + SQLAlchemy + Bootstrap.

## Requisitos
- Python 3.10+
- (Opcional) SQLite 3 (incluido con Python)

## Instalación rápida (Windows)
1. Crear entorno y activar:
```
python -m venv .venv
.venv\Scripts\activate
```
2. Instalar dependencias:
```
pip install --upgrade pip
pip install -r requirements.txt
```
3. Variables de entorno (ya provistas en `.env`):
```
FLASK_APP=fixu
FLASK_ENV=development
SECRET_KEY=dev-secret-change-me
SQLALCHEMY_DATABASE_URI=sqlite:///fixu.db
```
4. Base de datos (Flask-Migrate):
```
flask db init
flask db migrate -m "initial"
flask db upgrade
```
(La app también intentará crear tablas automáticamente si no existen para entorno de desarrollo.)

5. Datos de ejemplo (opcional):
```
flask seed
```

6. Ejecutar servidor:
```
flask run
```

## Accesos de prueba (datos seed por defecto)
- Admin: admin@fixu.local / admin123
- Agente: agent@fixu.local / agent123
- Solicitante: requester@fixu.local / requester123

## Estructura
- `fixu/`: paquete principal (app factory, modelos, blueprints)
- `fixu/templates/`: vistas Jinja
- `fixu/static/`: assets estáticos

## Funcionalidades
- Autenticación email/contraseña, roles: admin/agent/requester
- Tickets CRUD, filtros, paginación
- Comentarios con visibilidad pública/privada
- Equipos y miembros (agentes)
- Solicitantes (directorio)
- API dependiente: `/api/teams/<id>/members`

## Producción
- Configurar variables de entorno seguras (`SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`).
- Ejecutar migraciones en despliegue.
- Usar un servidor WSGI (gunicorn/uwsgi) y un reverse proxy (nginx/apache).
