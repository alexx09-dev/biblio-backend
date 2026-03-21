# main.py
# Punto de entrada principal de la aplicación FastAPI
# Biblioteca Personal API v2.0
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from exceptions.handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from logger import logger
from api.libros import router as libros_router
import os

# ---------------------------------------------------------------------------
# Instancia principal de FastAPI
# ---------------------------------------------------------------------------
is_dev = os.getenv("ENVIRONMENT") == "development"

app = FastAPI(
    title="Biblioteca Personal API",
    description="Backend REST para gestionar tu catálogo de libros personales. "
                "Soporta CRUD completo, búsqueda por texto y filtrado por género.",
    version="2.0.0",
    docs_url="/docs" if is_dev else None,
    redoc_url="/redoc" if is_dev else None,
    openapi_url="/openapi.json" if is_dev else None,
)

# ---------------------------------------------------------------------------
# Configuración de CORS
# ---------------------------------------------------------------------------
origins_permitidos = [
    "https://biblio-react-sandy.vercel.app",  # URL PUBLICA
    "http://localhost:4200",
    "http://localhost:5173",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Registro de handlers globales de excepciones
# ---------------------------------------------------------------------------
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ---------------------------------------------------------------------------
# Registro de routers
# ---------------------------------------------------------------------------
app.include_router(libros_router)

# ---------------------------------------------------------------------------
# Evento de inicio de la aplicación
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    logger.info("=" * 50)
    logger.info("🚀 Biblioteca Personal API iniciando...")
    logger.info("📚 Versión: 2.0.0")
    logger.info(f"🔧 Modo: {'desarrollo' if is_dev else 'producción'}")
    logger.info(f"📖 Documentación: {'habilitada en /docs' if is_dev else 'deshabilitada'}")
    logger.info(f"🔌 DB_HOST: {settings.DB_HOST}")
    logger.info(f"🔌 DB_PORT: {settings.DB_PORT}")
    logger.info(f"🔌 DB_USER: {settings.DB_USER}")
    logger.info(f"🔌 DB_NAME: {settings.DB_NAME}")
    logger.info("🌐 CORS habilitado para:")
    for origen in origins_permitidos:
        logger.info(f"   → {origen}")
    logger.info("=" * 50)

# ---------------------------------------------------------------------------
# Endpoint de prueba
# ---------------------------------------------------------------------------
@app.get("/", tags=["Status"])
def raiz():
    """
    Endpoint de bienvenida.
    Devuelve un JSON indicando que la API está en línea.
    """
    logger.info("Endpoint raíz consultado")
    return {
        "mensaje": "Biblioteca Personal API está activa",
        "version": "2.0.0",
    }
