# config.py
# Gestión centralizada de configuración con Pydantic Settings
# Todas las variables de entorno se leen y validan aquí

from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    """
    Clase de configuración tipada.
    Pydantic Settings lee automáticamente las variables del archivo .env
    y valida que tengan el tipo correcto al arrancar la aplicación.
    """

    # --- Variables de conexión a MySQL ---
    # Todas son obligatorias (no tienen valor por defecto)
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int        # Pydantic convierte automáticamente el string "3306" a int
    DB_NAME: str

    # --- Metadata de la aplicación ---
    APP_NAME: str = "Biblioteca Personal API"
    APP_VERSION: str = "2.0.0"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        Construye la URL de conexión a MySQL a partir de las variables individuales.
        Se calcula automáticamente, no se define en el .env.
        Ejemplo resultado: mysql+pymysql://root:admin@localhost:3306/biblioteca_db
        """
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        # Indica a Pydantic Settings que lea las variables desde este archivo
        env_file = ".env"
        env_file_encoding = "utf-8"


# ---------------------------------------------------------------------------
# Instancia única de Settings — se importa en todo el proyecto
# Al importar este módulo, Pydantic lee y valida el .env inmediatamente
# ---------------------------------------------------------------------------
settings = Settings()