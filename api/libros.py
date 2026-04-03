# api/libros.py
# Router de FastAPI para el recurso Libro

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from schemas import LibroRead, LibroCreate, LibroUpdate
from services.libro_service import (
    filtrar_libros,
    crear_libro,
    obtener_libro_por_id,
    actualizar_libro,
    eliminar_libro,
)
from services.auth_service import obtener_usuario_actual  # [FASE 5A]
from models.usuario import Usuario                        # [FASE 5A]
from logger import logger

router = APIRouter(
    prefix="/api/libros",
    tags=["Libros"],
)


@router.get("/", response_model=list[LibroRead])
def listar_libros(
    genero: Optional[str] = Query(
        default=None,
        description="Filtrar por género literario (ej: Terror, Juvenil)",
    ),
    busqueda: Optional[str] = Query(
        default=None,
        description="Buscar texto en título o autor (ej: garcia, cien años)",
    ),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),  # [FASE 5A]
):
    """
    Devuelve los libros del usuario autenticado con filtros opcionales.

    Requiere token JWT en el header: Authorization: Bearer <token>

    Ejemplos de uso:
    - GET /api/libros                             → todos mis libros
    - GET /api/libros?genero=Terror               → mis libros de Terror
    - GET /api/libros?busqueda=garcia             → búsqueda en mis libros
    - GET /api/libros?genero=Terror&busqueda=casa → combinado
    """
    logger.info(
        f"GET /api/libros → usuario_id={usuario_actual.id} "
        f"genero='{genero}' busqueda='{busqueda}'"
    )
    return filtrar_libros(
        db,
        usuario_id=usuario_actual.id,
        genero=genero,
        busqueda=busqueda,
    )


@router.post("/", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear_libro_endpoint(
    datos: LibroCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),  # [FASE 5A]
):
    """
    Crea un nuevo libro asociado al usuario autenticado.

    Requiere token JWT en el header: Authorization: Bearer <token>
    """
    logger.info(
        f"POST /api/libros → usuario_id={usuario_actual.id} "
        f"titulo='{datos.titulo}' autor='{datos.autor}'"
    )
    return crear_libro(db, datos, usuario_id=usuario_actual.id)


@router.get("/{id}", response_model=LibroRead)
def obtener_libro(
    id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),  # [FASE 5A]
):
    """
    Devuelve un libro del usuario autenticado por su id, con sinopsis.

    Requiere token JWT en el header: Authorization: Bearer <token>

    - Si el libro existe y pertenece al usuario → 200 con sinopsis
    - Si el libro no existe o pertenece a otro usuario → 404
    """
    logger.info(f"GET /api/libros/{id} → usuario_id={usuario_actual.id}")
    libro = obtener_libro_por_id(db, id, usuario_id=usuario_actual.id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún libro con id={id}",
        )
    return libro


@router.put("/{id}", response_model=LibroRead)
def actualizar_libro_endpoint(
    id: int,
    datos: LibroUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),  # [FASE 5A]
):
    """
    Actualiza parcialmente un libro del usuario autenticado.

    Requiere token JWT en el header: Authorization: Bearer <token>
    """
    logger.info(f"PUT /api/libros/{id} → usuario_id={usuario_actual.id}")
    libro = actualizar_libro(db, id, datos, usuario_id=usuario_actual.id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún libro con id={id}",
        )
    return libro


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_libro_endpoint(
    id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),  # [FASE 5A]
):
    """
    Elimina un libro del usuario autenticado por su id.

    Requiere token JWT en el header: Authorization: Bearer <token>

    - Si el libro existe y pertenece al usuario → lo elimina y devuelve confirmación
    - Si el libro no existe o pertenece a otro usuario → 404
    """
    logger.info(f"DELETE /api/libros/{id} → usuario_id={usuario_actual.id}")
    resultado = eliminar_libro(db, id, usuario_id=usuario_actual.id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún libro con id={id}",
        )
    return {"mensaje": f"Libro con id={id} eliminado correctamente"}