# services/libro_service.py
# Capa de servicios para la entidad Libro

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from models.libro import Libro
from schemas import LibroCreate, LibroUpdate
from logger import logger


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


def obtener_libro_por_id(db: Session, id: int) -> Optional[Libro]:
    """
    Busca y devuelve un libro por su id.
    Devuelve None si no existe.
    """
    libro = db.query(Libro).filter(Libro.id == id).first()
    if libro:
        logger.info(
            f"obtener_libro_por_id → encontrado: id={id} "
            f"titulo='{libro.titulo}'"
        )
    else:
        logger.warning(f"obtener_libro_por_id → no encontrado: id={id}")
    return libro


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


# [NUEVO]
def eliminar_libro(db: Session, id: int) -> Optional[bool]:
    """
    Elimina un libro de la base de datos por su id.

    Flujo:
    1. Busca el libro por id
    2. Si no existe → devuelve None (el endpoint lanzará 404)
    3. Elimina el objeto de la sesión
    4. Confirma la transacción → el DELETE se ejecuta en MySQL
    5. Devuelve True para indicar que la eliminación fue exitosa

    Args:
        db: Sesión activa de SQLAlchemy
        id: Id del libro a eliminar

    Returns:
        True si se eliminó correctamente, None si no existía
    """

    # Paso 1: verificar que el libro existe antes de intentar eliminarlo
    libro = db.query(Libro).filter(Libro.id == id).first()

    if not libro:
        logger.warning(f"eliminar_libro → no encontrado: id={id}")
        return None

    # Guardar el título para el log antes de eliminar el objeto
    titulo = libro.titulo

    # Paso 2: marcar el objeto para eliminación en la sesión
    # db.delete() registra la intención — aún no ejecuta el DELETE en MySQL
    db.delete(libro)

    # Paso 3: confirmar la transacción → ejecuta el DELETE en MySQL
    db.commit()

    logger.info(
        f"eliminar_libro → eliminado: id={id} titulo='{titulo}'"
    )

    # Devolvemos True para que el endpoint sepa que la operación fue exitosa
    return True