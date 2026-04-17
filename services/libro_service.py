# services/libro_service.py
# Capa de servicios para la entidad Libro

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import httpx

from models.libro import Libro
from schemas import LibroCreate, LibroUpdate
from logger import logger


# ---------------------------------------------------------
# UTILIDADES INTERNAS
# ---------------------------------------------------------

def _extraer_texto_descripcion(descripcion) -> Optional[str]:
    """
    Extrae el texto de una descripción de Open Library.
    Puede ser un string directo o un dict con clave 'value'.
    """
    if isinstance(descripcion, str):
        return descripcion.strip() or None
    if isinstance(descripcion, dict):
        texto = descripcion.get("value", "")
        return texto.strip() or None
    return None


def _es_espanol(texto: str) -> bool:
    """
    Heurística simple para detectar si un texto está en español.
    """
    indicadores = [
        " el ", " la ", " los ", " las ", " un ", " una ",
        " de ", " del ", " en ", " es ", " son ", " que ",
        " con ", " por ", " para ", " su ", " sus ",
        "ción", "mente", "ñ", "á", "é", "í", "ó", "ú", "¿", "¡"
    ]
    texto_lower = texto.lower()
    return any(ind in texto_lower for ind in indicadores)


# ---------------------------------------------------------
# INTEGRACIÓN EXTERNA
# ---------------------------------------------------------

def buscar_sinopsis_open_library(isbn: str) -> Optional[str]:
    """
    Busca la sinopsis de un libro en Open Library priorizando español.
    """

    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

    try:
        logger.info(f"Buscando sinopsis ISBN={isbn}")
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        libro_data = data.get(f"ISBN:{isbn}")
        if not libro_data:
            return None

        descripcion = libro_data.get("description")
        texto = _extraer_texto_descripcion(descripcion)

        if texto:
            return texto

    except Exception as e:
        logger.error(f"Error buscando sinopsis ISBN={isbn}: {e}")

    return None


# ---------------------------------------------------------
# CRUD
# ---------------------------------------------------------

def crear_libro(db: Session, libro: LibroCreate) -> Libro:
    nuevo_libro = Libro(**libro.dict())

    # Intentar enriquecer con sinopsis si hay ISBN
    if nuevo_libro.isbn:
        sinopsis = buscar_sinopsis_open_library(nuevo_libro.isbn)
        if sinopsis:
            nuevo_libro.descripcion = sinopsis

    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)

    return nuevo_libro


def obtener_libros(db: Session):
    return db.query(Libro).all()


def obtener_libro_por_id(db: Session, libro_id: int):
    return db.query(Libro).filter(Libro.id == libro_id).first()


def actualizar_libro(db: Session, libro_id: int, datos: LibroUpdate):
    libro = obtener_libro_por_id(db, libro_id)
    if not libro:
        return None

    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(libro, campo, valor)

    db.commit()
    db.refresh(libro)

    return libro


def eliminar_libro(db: Session, libro_id: int):
    libro = obtener_libro_por_id(db, libro_id)
    if not libro:
        return False

    db.delete(libro)
    db.commit()
    return True


# ---------------------------------------------------------
# FILTRO (SOLUCIONA TU ERROR)
# ---------------------------------------------------------

def filtrar_libros(db: Session, termino: str):
    """
    Filtra libros por título o autor (búsqueda parcial).
    """
    return db.query(Libro).filter(
        or_(
            Libro.titulo.ilike(f"%{termino}%"),
            Libro.autor.ilike(f"%{termino}%")
        )
    ).all()