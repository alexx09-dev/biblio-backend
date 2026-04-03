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
    1. Edición del ISBN → ¿tiene descripción en español? → usarla
    2. Work asociado → ¿tiene descripción en español? → usarla
    3. Ediciones del Work en español → ¿alguna tiene descripción? → usarla
    4. Fallback → descripción en inglés si no hay nada en español
    5. None si no hay nada
    """

    # ------------------------------------------------------------------
    # PASO 1: Consultar la edición directa por ISBN
    # ------------------------------------------------------------------
    url_isbn = (
        f"https://openlibrary.org/api/books"
        f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    )

    sinopsis_ingles = None

    try:
        logger.info(f"buscar_sinopsis_open_library → consultando ISBN={isbn}")
        response = httpx.get(url_isbn, timeout=5)
        response.raise_for_status()
        data = response.json()

        clave = f"ISBN:{isbn}"
        edicion_data = data.get(clave)

        if edicion_data:
            excerpts = edicion_data.get("excerpts")
            if excerpts and isinstance(excerpts, list):
                texto = excerpts[0].get("text", "").strip()
                if texto:
                    if _es_espanol(texto):
                        logger.info(f"buscar_sinopsis_open_library → excerpts en español ISBN={isbn}")
                        return texto
                    sinopsis_ingles = sinopsis_ingles or texto

            descripcion = edicion_data.get("description")
            if descripcion:
                texto = _extraer_texto_descripcion(descripcion)
                if texto:
                    if _es_espanol(texto):
                        logger.info(f"buscar_sinopsis_open_library → description en español ISBN={isbn}")
                        return texto
                    sinopsis_ingles = sinopsis_ingles or texto

    except httpx.TimeoutException:
        logger.error(f"buscar_sinopsis_open_library → timeout paso 1 ISBN={isbn}")
    except Exception as e:
        logger.error(f"buscar_sinopsis_open_library → error paso 1 ISBN={isbn}: {e}")

    # -----------------------------------------------------