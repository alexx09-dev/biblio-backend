# services/libro_service.py
# Capa de servicios para la entidad Libro

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

import httpx

from models.libro import Libro
from schemas import LibroCreate, LibroUpdate
from logger import logger


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
    Busca palabras funcionales comunes que no existen en inglés.
    """
    indicadores = [
        " el ", " la ", " los ", " las ", " un ", " una ",
        " de ", " del ", " en ", " es ", " son ", " que ",
        " con ", " por ", " para ", " una ", " su ", " sus ",
        "ción", "mente", "ñ", "á", "é", "í", "ó", "ú", "¿", "¡"
    ]
    texto_lower = texto.lower()
    return any(ind in texto_lower for ind in indicadores)


def buscar_sinopsis_open_library(isbn: str) -> Optional[str]:
    """
    Busca la sinopsis de un libro en Open Library priorizando español.

    Estrategia en orden:
    1. Consulta la edición del ISBN → si tiene descripción en español → usarla
    2. Obtiene el Work (obra) asociado → busca ediciones en español con descripción
    3. Si no hay nada en español → usa la descripción en inglés como fallback
    4. Si no hay nada → devuelve None

    Args:
        isbn: ISBN del libro (10 o 13 dígitos)

    Returns:
        Texto de la sinopsis (preferiblemente en español), o None
    """

    # ------------------------------------------------------------------
    # PASO 1: Consultar la edición directa por ISBN
    # ------------------------------------------------------------------
    url_isbn = (
        f"https://openlibrary.org/api/books"
        f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    )

    sinopsis_ingles = None  # guardamos el inglés como fallback

    try:
        logger.info(f"buscar_sinopsis_open_library → consultando ISBN={isbn}")
        response = httpx.get(url_isbn, timeout=5)
        response.raise_for_status()
        data = response.json()

        clave = f"ISBN:{isbn}"
        edicion_data = data.get(clave)

        if edicion_data:
            # Intentar excerpts primero
            excerpts = edicion_data.get("excerpts")
            if excerpts and isinstance(excerpts, list):
                texto = excerpts[0].get("text", "").strip()
                if texto:
                    if _es_espanol(texto):
                        logger.info(f"buscar_sinopsis_open_library → excerpts en español ISBN={isbn}")
                        return texto
                    sinopsis_ingles = sinopsis_ingles or texto

            # Intentar description
            descripcion = edicion_data.get("description")
            if descripcion:
                texto = _extraer_texto_descripcion(descripcion)
                if texto:
                    if _es_espanol(texto):
                        logger.info(f"buscar_sinopsis_open_library → description en español ISBN={isbn}")
                        return texto
                    sinopsis_ingles = sinopsis_ingles or texto

    except httpx.TimeoutException:
        logger.error(f"buscar_sinopsis_open_library → timeout en paso 1 ISBN={isbn}")
    except Exception as e:
        logger.error(f"buscar_sinopsis_open_library → error paso 1 ISBN={isbn}: {e}")

    # ------------------------------------------------------------------
    # PASO 2: Buscar el Work (obra) y explorar ediciones en español
    # ------------------------------------------------------------------
    try:
        logger.info(f"buscar_sinopsis_open_library → buscando Work para ISBN={isbn}")

        # Obtener el Work key desde la edición
        url_edition = f"https://openlibrary.org/isbn/{isbn}.json"
        resp_edition = httpx.get(url_edition, timeout=5)
        resp_edition.raise_for_status()
        edition_json = resp_edition.json()

        works = edition_json.get("works", [])
        if not works:
            logger.warning(f"buscar_sinopsis_open_library → sin Work asociado ISBN={isbn}")
            return sinopsis_ingles  # fallback inglés o None

        work_key = works[0].get("key")  # ej: "/works/OL12345W"
        if not work_key:
            return sinopsis_ingles

        # Obtener la descripción del Work directamente
        url_work = f"https://openlibrary.org{work_key}.json"
        resp_work = httpx.get(url_work, timeout=5)
        resp_work.raise_for_status()
        work_json = resp_work.json()

        descripcion_work = work_json.get("description")
        if descripcion_work:
            texto = _extraer_texto_descripcion(descripcion_work)
            if texto:
                if _es_espanol(texto):
                    logger.info(f"buscar_sinopsis_open_library → descripción Work en español ISBN={isbn}")
                    return texto
                sinopsis_ingles = sinopsis_ingles or texto

        # Buscar ediciones del Work filtrando por idioma español
        url_ediciones = (
            f"https://openlibrary.org{work_key}/editions.json"
            f"?limit=10"
        )
        resp_ediciones = httpx.get(url_ediciones, timeout=5)
        resp_ediciones.raise_for_status()
        ediciones_json = resp_ediciones.json()

        ediciones = ediciones_json.get("entries", [])

        for edicion in ediciones:
            # Filtrar ediciones marcadas como español
            idiomas = edicion.get("languages", [])
            es_espanol_edicion = any(
                "/languages/spa" in lang.get("key", "")
                for lang in idiomas
            )

            descripcion = edicion.get("description") or edicion.get("first_sentence")
            if not descripcion:
                continue

            texto = _extraer_texto_descripcion(descripcion)
            if not texto:
                continue

            # Si la edición está marcada en español → usarla directamente
            if es_espanol_edicion:
                logger.info(f"buscar_sinopsis_open_library → edición en español encontrada ISBN={isbn}")
                return texto

            # Si no está marcada pero el texto parece español → usarla
            if _es_espanol(texto):
                logger.info(f"buscar_sinopsis_open_library → texto en español detectado ISBN={isbn}")
                return texto

            # Guardar como fallback inglés si no tenemos nada aún
            sinopsis_ingles = sinopsis_ingles or texto

    except httpx.TimeoutException:
        logger.error(f"buscar_sinopsis_open_library → timeout en paso 2 ISBN={isbn}")
    except Exception as e:
        logger.error(f"buscar_sinopsis_open_library → error paso 2 ISBN={isbn}: {e}")

    # ------------------------------------------------------------------
    # PASO 3: Fallback — devolver inglés si no encontramos español
    # ------------------------------------------------------------------
    if sinopsis_ingles:
        logger.info(f"buscar_sinopsis_open_library → fallback inglés ISBN={isbn}")
    else:
        logger.warning(f"buscar_sinopsis_open_library → sin sinopsis disponible ISBN={isbn}")

    return sinopsis_ingles


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
    Busca un libro por su id y enriquece la respuesta con sinopsis.

    Flujo:
    1. Busca el libro en BD → si no existe devuelve None
    2. Si tiene ISBN → busca sinopsis priorizando español en Open Library
    3. Devuelve dict completo con sinopsis lista para mostrar
    """
    libro = db.query(Libro).filter(Libro.id == id).first()

    if not libro:
        logger.warning(f"obtener_libro_por_id → no encontrado: id={id}")
        return None

    logger.info(f"obtener_libro_por_id → encontrado: id={id} titulo='{libro.titulo}'")

    sinopsis = None
    if libro.isbn:
        sinopsis = buscar_sinopsis_open_library(libro.isbn)

    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "isbn": libro.isbn,
        "genero": libro.genero,
        "anio": libro.anio,
        "rating": libro.rating,
        "sinopsis": sinopsis,
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