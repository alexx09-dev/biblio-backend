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
from api.auth import router as auth_router
from database import Base, engine

# 🔥 IMPORTAR MODELOS (NECESARIO PARA ALEMBIC TAMBIÉN)
from models.usuario import Usuario
from models.libro import Libro

import os

is_dev = os.getenv("ENVIRONMENT") == "development"

app = FastAPI(
    title="Biblioteca Personal API",
    description="Backend REST para gestionar tu catálogo de libros personales.",
    version="2.0.0",
    docs_url="/docs" if is_dev else None,
    redoc_url="/redoc" if is_dev else None,
    openapi_url="/openapi.json" if is_dev else None,
)

origins_permitidos = [
    "https://biblio-react-sandy.vercel.app",
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

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(libros_router)
app.include_router(auth_router)


@app.on_event("startup")
async def startup():
    logger.info("=" * 50)
    logger.info("🚀 Biblioteca Personal API iniciando...")
    logger.info("📚 Versión: 2.0.0")
    logger.info(f"🔧 Modo: {'desarrollo' if is_dev else 'producción'}")
    logger.info("🐘 Base de datos: PostgreSQL (Neon)")
    logger.info("=" * 50)


@app.get("/", tags=["Status"])
def raiz():
    return {
        "mensaje": "Biblioteca Personal API está activa",
        "version": "2.0.0",
    }