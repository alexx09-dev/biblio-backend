from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str              # Neon (destino)
    OLD_DATABASE_URL: str          # MySQL (origen)

    SECRET_KEY: str = "Mdgiwandhwdgmadgwadg"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    APP_NAME: str = "Biblioteca Personal API"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

settings = Settings()