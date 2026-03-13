# schemas.py
# Esquemas Pydantic v2 para validación de entrada y salida de la API
# Separar esquemas por responsabilidad evita exponer datos internos
# y permite validaciones distintas para crear vs actualizar vs leer

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
import datetime


class LibroBase(BaseModel):
    """
    Esquema base con los campos comunes a Create y Read.
    Contiene las validaciones principales del negocio.
    """

    # --- Campos obligatorios ---
    titulo: str
    autor: str
    rating: int

    # --- Campos opcionales ---
    isbn: Optional[str] = None
    genero: Optional[str] = None
    anio: Optional[int] = None

    # ------------------------------------------------------------------
    # Validaciones de negocio con field_validator (sintaxis Pydantic v2)
    # ------------------------------------------------------------------

    @field_validator("titulo", "autor")
    @classmethod
    def no_vacio(cls, valor: str) -> str:
        """
        Verifica que titulo y autor no sean cadenas vacías o solo espacios.
        Un título de " " no es válido aunque técnicamente sea un string.
        """
        if not valor or not valor.strip():
            raise ValueError("Este campo no puede estar vacío")
        return valor.strip()

    @field_validator("rating")
    @classmethod
    def rating_valido(cls, valor: int) -> int:
        """
        Verifica que el rating esté entre 1 y 5 inclusive.
        """
        if valor < 1 or valor > 5:
            raise ValueError("El rating debe ser un número entre 1 y 5")
        return valor

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, valor: Optional[int]) -> Optional[int]:
        """
        Si se provee el año, verifica que sea un valor razonable.
        Mínimo 1000 (primeros libros impresos) y máximo el año actual.
        """
        if valor is not None:
            anio_actual = datetime.datetime.now().year
            if valor < 1000 or valor > anio_actual:
                raise ValueError(
                    f"El año debe estar entre 1000 y {anio_actual}"
                )
        return valor


class LibroCreate(LibroBase):
    """
    Esquema para crear un libro (POST).
    Hereda todas las validaciones de LibroBase.
    No incluye 'id' porque MySQL lo genera automáticamente.
    """
    pass


class LibroUpdate(BaseModel):
    """
    Esquema para actualizar un libro (PUT).
    Todos los campos son Optional para permitir actualización parcial:
    el cliente envía solo los campos que quiere modificar.
    Los campos no enviados conservan su valor actual en la BD.
    """

    titulo: Optional[str] = None
    autor: Optional[str] = None
    rating: Optional[int] = None
    isbn: Optional[str] = None
    genero: Optional[str] = None
    anio: Optional[int] = None

    # Reutilizamos las mismas validaciones — solo se aplican si el campo viene
    @field_validator("titulo", "autor")
    @classmethod
    def no_vacio(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None and not valor.strip():
            raise ValueError("Este campo no puede estar vacío")
        return valor.strip() if valor else valor

    @field_validator("rating")
    @classmethod
    def rating_valido(cls, valor: Optional[int]) -> Optional[int]:
        if valor is not None and (valor < 1 or valor > 5):
            raise ValueError("El rating debe ser un número entre 1 y 5")
        return valor

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, valor: Optional[int]) -> Optional[int]:
        if valor is not None:
            anio_actual = datetime.datetime.now().year
            if valor < 1000 or valor > anio_actual:
                raise ValueError(
                    f"El año debe estar entre 1000 y {anio_actual}"
                )
        return valor


class LibroRead(LibroBase):
    """
    Esquema para leer/devolver un libro (respuesta de la API).
    Hereda todos los campos de LibroBase y agrega 'id'.

    model_config con from_attributes=True (antes orm_mode=True en Pydantic v1)
    permite convertir objetos ORM de SQLAlchemy directamente a este esquema.
    """

    id: int

    # Sintaxis Pydantic v2 — reemplaza: class Config: orm_mode = True
    model_config = ConfigDict(from_attributes=True)