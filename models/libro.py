# models/libro.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Libro(Base):
    __tablename__ = "libros"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    titulo      = Column(String(255), nullable=False)
    autor       = Column(String(255), nullable=False)
    rating      = Column(Integer, nullable=False)
    isbn        = Column(String(20), nullable=True)
    genero      = Column(String(100), nullable=True)
    anio        = Column(Integer, nullable=True)
    sinopsis    = Column(String(2000), nullable=True)

    # [FASE 7A] Interruptor de favorito — True = marcado, False = normal
    # default=False → ningún libro nace como favorito
    # server_default="0" → MySQL pone 0 (falso) en filas que ya existen
    es_favorito = Column(Boolean, default=False, server_default="false", nullable=False)

    # Relación con usuario
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario     = relationship("Usuario", back_populates="libros")