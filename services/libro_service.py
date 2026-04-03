# services/libro_service.py
# Capa de servicios para la entidad Libro

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

import httpx  # [FASE 4A]

from models.libro import Libro
from schemas import LibroCreate, LibroUpdate
from logger import logger


# [FASE 4A] -------------------------------------------------------------------
def buscar_sinopsis_open_library(isbn: str) -> Optional[str]:
    """
    Consulta Open Library para obtener la sinopsis de un libro por ISBN.

    Estrategia:
    1. Intenta extraer 'excerpts[0].text' (fragmento editorial)
    2. Si no hay, intenta 'description' (puede ser str o dict con 'value')
    3. Si no hay nada o hay error → devuelve None

    Timeout de 5 segundos para no bloquear el endpoint si Open Library tarda.
    """
    url = (
        f"https://openlibrary.org/api/books"
        f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    )

    try:
        logger.info(f"buscar_sinopsis_open_library → consultando ISBN={isbn}")
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        clave = f"ISBN:{isbn}"
        libro_data = data.get(clave)

        if not libro_data:
            logger.warning(
                f"buscar_sinopsis_open_library → ISBN={isbn} no encontrado en Open Library"
            )
            return None

        # Intento 1: excerpts (fragmento editorial)
        excerpts = libro_data.get("excerpts")
        if excerpts and isinstance(excerpts, list):
            texto = excerpts[0].get("text")
            if texto:
                logger.info(
                    f"buscar_sinopsis_open_library → sinopsis desde 'excerpts' ISBN={isbn}"
                )
                return texto

        # Intento 2: description (str o dict)
        description = libro_data.get("description")
        if description:
            if isinstance(description, str):
                logger.info(
                    f"buscar_sinopsis_open_library → sinopsis desde 'description' (str) ISBN={isbn}"
                )
                return description
            if isinstance(description, dict):
                texto = description.get("value")
                if texto:
                    logger.info(
                        f"buscar_sinopsis_open_library → sinopsis desde 'description' (dict) ISBN={isbn}"
                    )
                    return texto

        logger.warning(
            f"buscar_sinopsis_open_library → sin sinopsis disponible para ISBN={isbn}"
        )
        return None

    except httpx.TimeoutException:
        logger.error(
            f"buscar_sinopsis_open_library → timeout al consultar ISBN={isbn}"
        )
        return None
    except Exception as e:
        logger.error(
            f"buscar_sinopsis_open_library → error inesperado ISBN={isbn}: {e}"
        )
        return None
# [FIN FASE 4A] ---------------------------------------------------------------


def listar_libros(db: Session) -> list[Libro]:
    """
    Devuelve todos los libros de la base de datos sin filtros.
    """
    libros = db.query(Libro).all()
    logger.info(f"listar_libros → {len(libros)} libro(s) encontrado(s)")
    return libros


def filtrar_libros(
    db: Session,
    genero: Optional[str] = None,
    busqueda: Optional[str] = None,
) -> list[Libro]:
    """
    Devuelve libros aplicando filtros opcionales de forma dinámica.
    """
    query = db.query(Libro)

    if genero:
        query = query.filter(Libro.genero.ilike(genero))
        logger.debug(f"filtrar_libros → filtro género: '{genero}'")

    if busqueda:
        termino = f"%{busqueda}%"
        query = query.filter(
            or_(
                Libro.titulo.ilike(termino),
                Libro.autor.ilike(termino),
            )
        )
        logger.debug(f"filtrar_libros → filtro búsqueda: '{busqueda}'")

    libros = query.all()
    logger.info(
        f"filtrar_libros → género='{genero}' busqueda='{busqueda}' "
        f"→ {len(libros)} resultado(s)"
    )
    return libros


def crear_libro(db: Session, datos: LibroCreate) -> Libro:
    """
    Crea un nuevo libro en la base de datos.
    """
    datos_dict = datos.model_dump()
    nuevo_libro = Libro(**datos_dict)
    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)
    logger.info(
        f"crear_libro → libro creado: id={nuevo_libro.id} "
        f"titulo='{nuevo_libro.titulo}' autor='{nuevo_libro.autor}'"
    )
    return nuevo_libro


def obtener_libro_por_id(db: Session, id: int) -> Optional[dict]:
    """
    Busca un libro por su id y enriquece la respuesta con sinopsis de Open Library.

    Flujo:
    1. Busca el libro en BD → si no existe devuelve None
    2. Si tiene ISBN → consulta Open Library en tiempo real
    3. Construye y devuelve un dict con todos los campos + 'sinopsis'

    El dict es compatible con LibroRead gracias a from_attributes=True.
    """
    libro = db.query(Libro).filter(Libro.id == id).first()

    if not libro:
        logger.warning(f"obtener_libro_por_id → no encontrado: id={id}")
        return None

    logger.info(
        f"obtener_libro_por_id → encontrado: id={id} titulo='{libro.titulo}'"
    )

    # [FASE 4A] Consultar sinopsis si hay ISBN, sino None directamente
    sinopsis = None
    if libro.isbn:
        sinopsis = buscar_sinopsis_open_library(libro.isbn)

    # Construir dict enriquecido — Pydantic lo valida con from_attributes=True
    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "isbn": libro.isbn,
        "genero": libro.genero,
        "anio": libro.anio,
        "rating": libro.rating,
        "sinopsis": sinopsis,  # [FASE 4A]
    }


def actualizar_libro(
    db: Session,
    id: int,
    datos: LibroUpdate,
) -> Optional[Libro]:
    """
    Actualiza parcialmente un libro existente.
    Solo modifica los campos enviados por el cliente.
    """
    libro = db.query(Libro).filter(Libro.id == id).first()

    if not libro:
        logger.warning(f"actualizar_libro → no encontrado: id={id}")
        return None

    campos_a_actualizar = datos.model_dump(exclude_unset=True)
    logger.debug(
        f"actualizar_libro → id={id} campos recibidos: {list(campos_a_actualizar.keys())}"
    )

    for campo, valor in campos_a_actualizar.items():
        setattr(libro, campo, valor)

    db.commit()
    db.refresh(libro)
    logger.info(
        f"actualizar_libro → actualizado: id={id} "
        f"campos={list(campos_a_actualizar.keys())}"
    )
    return libro


def eliminar_libro(db: Session, id: int) -> Optional[bool]:
    """
    Elimina un libro de la base de datos por su id.

    Flujo:
    1. Busca el libro por id
    2. Si no existe → devuelve None (el endpoint lanzará 404)
    3. Elimina el objeto de la sesión y confirma la transacción
    4. Devuelve True para indicar éxito
    """
    libro = db.query(Libro).filter(Libro.id == id).first()

    if not libro:
        logger.warning(f"eliminar_libro → no encontrado: id={id}")
        return None

    titulo = libro.titulo
    db.delete(libro)
    db.commit()

    logger.info(f"eliminar_libro → eliminado: id={id} titulo='{titulo}'")
    return True