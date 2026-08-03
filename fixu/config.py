import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

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

    # JWT para la App Móvil
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXP_HOURS = int(os.environ.get('JWT_EXP_HOURS', '12'))

    # Redis para Rate Limiting global
    REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

    # Subida de fotos de tickets (App Móvil)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads/tickets')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB por request

    # URL pública (nginx en el servidor público) usada para construir enlaces
    # absolutos a archivos estáticos (fotos de tickets) devueltos a la App Móvil.
    # Las peticiones llegan a Flask vía bridge_api con Host interno
    # (ej. flask_app_1:5000), así que url_for(..., _external=True) generaría
    # una URL no alcanzable desde el teléfono si no se fija explícitamente.
    PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', 'http://localhost')
