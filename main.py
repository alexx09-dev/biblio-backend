# main.py
# Punto de entrada principal de la aplicación FastAPI
# Biblioteca Personal API v2.0

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware  # [NUEVO]
from exceptions.handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from logger import logger
from api.libros import router as libros_router

# ---------------------------------------------------------------------------
# Instancia principal de FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Biblioteca Personal API",
    description="Backend REST para gestionar tu catálogo de libros personales. "
                "Soporta CRUD completo, búsqueda por texto y filtrado por género.",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# [NUEVO] Configuración de CORS
# Debe registrarse ANTES que los routers para que aplique a todas las rutas
#
# allow_origins: lista de dominios del frontend autorizados a consumir la API
# allow_methods: métodos HTTP permitidos desde el frontend
# allow_headers: headers HTTP que el frontend puede enviar
# allow_credentials: permite enviar cookies y headers de autenticación
# ---------------------------------------------------------------------------
origins_permitidos = [
    "http://localhost:4200",   # Angular (ng serve usa el puerto 4200 por defecto)
    "http://localhost:5173",   # React + Vite (vite dev server usa 5173 por defecto)
    "http://localhost:3000",   # React + Create React App (puerto 3000)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_permitidos,
    allow_credentials=True,
    allow_methods=["*"],       # Permite GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],       # Permite Content-Type, Authorization, etc.
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
    logger.info("📖 Documentación disponible en: /docs")
    logger.info("🌐 CORS habilitado para:")           # [NUEVO]
    for origen in origins_permitidos:                 # [NUEVO]
        logger.info(f"   → {origen}")                 # [NUEVO]
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
        "docs": "/docs",
    }