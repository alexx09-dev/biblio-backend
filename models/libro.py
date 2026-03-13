# models/libros.py
# Modelo ORM que representa la tabla 'libros' en MySQL
# SQLAlchemy usa esta clase para generar la tabla y construir las consultas

from sqlalchemy import Column, Integer, String
from database import Base


class Libro(Base):
    """
    Modelo ORM para la tabla 'libros'.
    Cada instancia de esta clase representa una fila en la tabla.
    """

    # Nombre de la tabla en MySQL
    __tablename__ = "libros"

    # ------------------------------------------------------------------
    # Campos obligatorios (nullable=False es el valor por defecto)
    # Si se intenta guardar un Libro sin estos campos, MySQL rechaza el registro
    # ------------------------------------------------------------------

    # Clave primaria autoincremental — MySQL asigna el valor automáticamente
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Título del libro — obligatorio, no puede ser NULL en la BD
    titulo = Column(String(255), nullable=False)

    # Autor del libro — obligatorio, no puede ser NULL en la BD
    autor = Column(String(255), nullable=False)

    # Puntuación personal del 1 al 5 — obligatorio
    rating = Column(Integer, nullable=False)

    # ------------------------------------------------------------------
    # Campos opcionales (nullable=True)
    # No todos los libros tienen ISBN conocido, género catalogado o año registrado
    # Guardar NULL es preferible a guardar cadenas vacías o valores inventados
    # ------------------------------------------------------------------

    # ISBN del libro — opcional, se usa para obtener portadas de Open Library
    # Ejemplo: "978-0-06-112008-4"
    isbn = Column(String(20), nullable=True)

    # Género literario — opcional, ej: Terror, Juvenil, Ciencia Ficción
    genero = Column(String(100), nullable=True)

    # Año de publicación — opcional, ej: 1985
    anio = Column(Integer, nullable=True)