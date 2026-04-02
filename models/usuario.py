# models/usuario.py
from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    nombre           = Column(String(100), nullable=False)
    email            = Column(String(255), nullable=False, unique=True)
    password_hash    = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    foto_perfil      = Column(String(500), nullable=True)
    avatar_config    = Column(Text, nullable=True)
    bio              = Column(String(500), nullable=True)
    generos_favoritos = Column(String(500), nullable=True)  # ← NUEVO

    libros = relationship("Libro", back_populates="usuario")