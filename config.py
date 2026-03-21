# config.py
# Gestión centralizada de configuración con Pydantic Settings
# Todas las variables de entorno se leen y validan aquí
from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    """
    Clase de configuración tipada.
    Pydantic Settings lee automáticamente las variables del entorno
    y valida que tengan el tipo correcto al arrancar la aplicación.
    """
    # --- Variables de conexión a MySQL ---
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # --- Metadata de la aplicación ---
    APP_NAME: str = "Biblioteca Personal API"
    APP_VERSION: str = "2.0.0"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

settings = Settings()
