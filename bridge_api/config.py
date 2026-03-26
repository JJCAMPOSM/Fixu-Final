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
    
    # API Keys para autenticación entre servicios
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "internal-secret-key")
    
    # Base de datos (compartida con Flask)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://fixu_user:fixu_password@db:5432/fixu"
    )
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada de settings."""
    return Settings()
