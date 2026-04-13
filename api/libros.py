# api/libros.py
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from schemas import LibroRead, LibroCreate, LibroUpdate, FavoritoUpdate
from services.libro_service import (
    filtrar_libros,
    crear_libro,
    obtener_libro_por_id,
    actualizar_libro,
    eliminar_libro,
)
from services.auth_service import obtener_usuario_actual
from models.usuario import Usuario
from models.libro import Libro
from logger import logger

router = APIRouter(
    prefix="/api/libros",
    tags=["Libros"],
)


@router.get("/", response_model=list[LibroRead])
def listar_libros(
    genero: Optional[str] = Query(default=None),
    busqueda: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    logger.info(f"GET /api/libros → usuario_id={usuario_actual.id}")
    return filtrar_libros(db, usuario_id=usuario_actual.id, genero=genero, busqueda=busqueda)


@router.post("/", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear_libro_endpoint(
    datos: LibroCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    logger.info(f"POST /api/libros → usuario_id={usuario_actual.id}")
    return crear_libro(db, datos, usuario_id=usuario_actual.id)


@router.get("/{id}", response_model=LibroRead)
def obtener_libro(
    id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    logger.info(f"GET /api/libros/{id} → usuario_id={usuario_actual.id}")
    libro = obtener_libro_por_id(db, id, usuario_id=usuario_actual.id)
    if not libro:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún libro con id={id}")
    return libro


@router.put("/{id}", response_model=LibroRead)
def actualizar_libro_endpoint(
    id: int,
    datos: LibroUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    logger.info(f"PUT /api/libros/{id} → usuario_id={usuario_actual.id}")
    libro = actualizar_libro(db, id, datos, usuario_id=usuario_actual.id)
    if not libro:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún libro con id={id}")
    return libro


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_libro_endpoint(
    id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    logger.info(f"DELETE /api/libros/{id} → usuario_id={usuario_actual.id}")
    resultado = eliminar_libro(db, id, usuario_id=usuario_actual.id)
    if not resultado:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún libro con id={id}")
    return {"mensaje": f"Libro con id={id} eliminado correctamente"}


@router.patch("/{id}/favorito", response_model=LibroRead)
def toggle_favorito(
    id: int,
    datos: FavoritoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    libro = db.query(Libro).filter(
        Libro.id == id,
        Libro.usuario_id == usuario_actual.id
    ).first()

    if not libro:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún libro con id={id}")

    libro.es_favorito = datos.es_favorito
    db.commit()
    db.refresh(libro)

    return {
        "id":          libro.id,
        "titulo":      libro.titulo,
        "autor":       libro.autor,
        "rating":      libro.rating,
        "isbn":        libro.isbn,
        "genero":      libro.genero,
        "anio":        libro.anio,
        "sinopsis":    None,
        "es_favorito": libro.es_favorito,
    }