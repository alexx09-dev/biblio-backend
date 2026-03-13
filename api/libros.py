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
    eliminar_libro,          # [NUEVO]
)
from logger import logger

# ---------------------------------------------------------------------------
# Router con prefijo /api/libros
# ---------------------------------------------------------------------------
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
):
    """
    Devuelve la lista de libros con filtros opcionales.

    Ejemplos de uso:
    - GET /api/libros                             → todos los libros
    - GET /api/libros?genero=Terror               → filtrado por género
    - GET /api/libros?busqueda=garcia             → búsqueda por título o autor
    - GET /api/libros?genero=Terror&busqueda=casa → combinado
    """
    logger.info(f"GET /api/libros → genero='{genero}' busqueda='{busqueda}'")
    return filtrar_libros(db, genero=genero, busqueda=busqueda)


@router.post(
    "/",
    response_model=LibroRead,
    status_code=status.HTTP_201_CREATED,
)
def crear_libro_endpoint(
    datos: LibroCreate,
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo libro en la biblioteca.

    Campos obligatorios: titulo, autor, rating (entre 1 y 5)
    Campos opcionales: isbn, genero, anio
    """
    logger.info(
        f"POST /api/libros → titulo='{datos.titulo}' autor='{datos.autor}'"
    )
    return crear_libro(db, datos)


@router.get("/{id}", response_model=LibroRead)
def obtener_libro(
    id: int,
    db: Session = Depends(get_db),
):
    """
    Devuelve un libro específico por su id.

    - Si el libro existe → devuelve el objeto con status 200
    - Si el libro no existe → devuelve error 404
    """
    logger.info(f"GET /api/libros/{id}")
    libro = obtener_libro_por_id(db, id)
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
):
    """
    Actualiza parcialmente un libro existente.
    Solo se modifican los campos enviados en el body.
    """
    logger.info(f"PUT /api/libros/{id}")
    libro = actualizar_libro(db, id, datos)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún libro con id={id}",
        )
    return libro


# [NUEVO]
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_libro_endpoint(
    id: int,
    db: Session = Depends(get_db),
):
    """
    Elimina un libro de la biblioteca por su id.

    - Si el libro existe → lo elimina y devuelve mensaje de confirmación
    - Si el libro no existe → devuelve error 404

    No requiere body en el request.
    La eliminación es permanente — no hay papelera de reciclaje.
    """
    logger.info(f"DELETE /api/libros/{id}")

    # Llamar al servicio de eliminación
    resultado = eliminar_libro(db, id)

    # Si el servicio devuelve None, el libro no existía → 404
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún libro con id={id}",
        )

    # Confirmar la eliminación con un mensaje descriptivo
    return {"mensaje": f"Libro con id={id} eliminado correctamente"}