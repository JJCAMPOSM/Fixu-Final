from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # App
    APP_NAME: str = "Fixu Bridge API"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # URLs de servicios
    FLASK_APP_URL: str = os.getenv("FLASK_APP_URL", "http://flask_app:5000")
    LARAVEL_ADMIN_URL: str = os.getenv("LARAVEL_ADMIN_URL", "http://laravel_admin:80")
    
    # API Keys para autenticación entre servicios. Sin default: si la env var
    # falta, pydantic-settings falla al arrancar en vez de aceptar un secreto
    # público conocido (compartido con fixu/config.py y Laravel).
    INTERNAL_API_KEY: str
    HMAC_SECRET_KEY: str

    # Base de datos (compartida con Flask). Sin default: una contraseña de
    # Postgres predecible (fixu_password) no debe poder colarse en producción.
    DATABASE_URL: str

    # Redis para Rate Limiting global (compartido con las réplicas de Flask)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada de settings."""
    return Settings()
