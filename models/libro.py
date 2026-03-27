# models/libro.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Libro(Base):
    __tablename__ = "libros"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    titulo     = Column(String(255), nullable=False)
    autor      = Column(String(255), nullable=False)
    rating     = Column(Integer, nullable=False)
    isbn       = Column(String(20), nullable=True)
    genero     = Column(String(100), nullable=True)
    anio       = Column(Integer, nullable=True)
    sinopsis   = Column(String(2000), nullable=True)

    # Relación con usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario    = relationship("Usuario", back_populates="libros")