import os


def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"La variable de entorno {name} es obligatoria y no está definida. "
            f"Copia .env.example a .env y define un valor único y aleatorio."
        )
    return value


class Config:
    SECRET_KEY = _require_env('SECRET_KEY')

    # Cookie de sesión: no accesible por JS, no enviada por HTTP plano
    # (excepto en desarrollo local, donde no hay HTTPS disponible).
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'https')

    # Soporte para PostgreSQL (Render y Docker)
    db_uri = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///fixu.db')
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # URL del panel de administración Laravel
    LARAVEL_ADMIN_URL = os.environ.get('LARAVEL_ADMIN_URL', 'http://localhost:8000')

    # JWT para la App Móvil (secreto independiente de SECRET_KEY: si uno se
    # filtra, el otro sigue protegido)
    JWT_SECRET_KEY = _require_env('JWT_SECRET_KEY')
    JWT_EXP_HOURS = int(os.environ.get('JWT_EXP_HOURS', '12'))

    # Compartidos con bridge_api/laravel_admin para firmar/validar llamadas
    # internas (HMAC de sync, API key de bridge, handoff de /admin). Sin
    # default: si falta cualquiera de los tres servicios firmaría/validaría
    # con secretos distintos y fallaría de forma ruidosa en vez de aceptar
    # silenciosamente un secreto público conocido.
    HMAC_SECRET_KEY = _require_env('HMAC_SECRET_KEY')
    INTERNAL_API_KEY = _require_env('INTERNAL_API_KEY')

    # Cifrado simétrico (Fernet/AES) de campos sensibles en reposo (ej. teléfono
    # del solicitante). Distinto del hasheo de contraseñas: aquí necesitamos
    # poder recuperar el valor original. Generar con:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY = _require_env('ENCRYPTION_KEY')

    # Redis para Rate Limiting global
    REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

    # Subida de fotos de tickets (App Móvil). Debe vivir FUERA de static/: Flask
    # registra automáticamente la ruta /static/<path:filename> sin autenticación,
    # así que si UPLOAD_FOLDER estuviera dentro de static/ cualquiera con el
    # nombre de archivo podría descargar la foto sin pasar por el control de
    # acceso de /api/uploads/tickets/<filename>.
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads/tickets')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB por request

    # URL pública (nginx en el servidor público) usada para construir enlaces
    # absolutos a archivos estáticos (fotos de tickets) devueltos a la App Móvil.
    # Las peticiones llegan a Flask vía bridge_api con Host interno
    # (ej. flask_app_1:5000), así que url_for(..., _external=True) generaría
    # una URL no alcanzable desde el teléfono si no se fija explícitamente.
    PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', 'http://localhost')
