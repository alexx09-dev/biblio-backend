# exceptions/handlers.py
# Manejadores globales de excepciones para la API
# Centralizan el formato de todos los errores en una estructura consistente:
# { "status": int, "mensaje": str, "detalle": str }

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Captura todas las HTTPException lanzadas en los endpoints.
    Ejemplos: 404 cuando no se encuentra un libro, 400 para datos inválidos.

    Sin este handler, FastAPI devuelve: {"detail": "mensaje"}
    Con este handler, devuelve la estructura estándar del proyecto.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "mensaje": obtener_mensaje_http(exc.status_code),
            "detalle": exc.detail,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Captura errores de validación de Pydantic (RequestValidationError).
    Se activa cuando el body o los query params no cumplen las validaciones
    definidas en los esquemas (ej: rating fuera de rango, título vacío).

    Formatea la lista de errores de Pydantic en un string legible.
    """
    # Construir un mensaje legible con todos los errores de validación
    errores = []
    for error in exc.errors():
        # 'loc' indica dónde ocurrió el error, ej: ('body', 'rating')
        campo = " → ".join(str(parte) for parte in error["loc"] if parte != "body")
        mensaje = error["msg"].replace("Value error, ", "")
        errores.append(f"{campo}: {mensaje}" if campo else mensaje)

    detalle = " | ".join(errores)

    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "mensaje": "Error de validación en los datos enviados",
            "detalle": detalle,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Captura cualquier excepción no controlada (error 500).
    Evita que errores internos expongan información sensible al cliente.
    En producción, este handler es la última línea de defensa.
    """
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "mensaje": "Error interno del servidor",
            "detalle": "Ocurrió un error inesperado. Por favor intenta más tarde.",
        },
    )


def obtener_mensaje_http(status_code: int) -> str:
    """
    Devuelve un mensaje amigable según el código de estado HTTP.
    Centraliza los mensajes para que sean consistentes en toda la API.
    """
    mensajes = {
        400: "Solicitud incorrecta",
        401: "No autorizado",
        403: "Acceso prohibido",
        404: "Recurso no encontrado",
        405: "Método no permitido",
        409: "Conflicto con el estado actual del recurso",
        422: "Error de validación en los datos enviados",
        500: "Error interno del servidor",
    }
    return mensajes.get(status_code, "Error en la solicitud")