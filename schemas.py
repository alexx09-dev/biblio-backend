# schemas.py
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from typing import Optional
import datetime
from datetime import date


class LibroBase(BaseModel):
    titulo: str
    autor: str
    rating: int
    isbn: Optional[str] = None
    genero: Optional[str] = None
    anio: Optional[int] = None
    sinopsis: Optional[str] = None  # ← AGREGADO

    @field_validator("titulo", "autor")
    @classmethod
    def no_vacio(cls, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValueError("Este campo no puede estar vacío")
        return valor.strip()

    @field_validator("rating")
    @classmethod
    def rating_valido(cls, valor: int) -> int:
        if valor < 1 or valor > 5:
            raise ValueError("El rating debe ser un número entre 1 y 5")
        return valor

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, valor: Optional[int]) -> Optional[int]:
        if valor is not None:
            anio_actual = datetime.datetime.now().year
            if valor < 1000 or valor > anio_actual:
                raise ValueError(f"El año debe estar entre 1000 y {anio_actual}")
        return valor


class LibroCreate(LibroBase):
    pass


class LibroUpdate(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None
    rating: Optional[int] = None
    isbn: Optional[str] = None
    genero: Optional[str] = None
    anio: Optional[int] = None
    sinopsis: Optional[str] = None  # ← AGREGADO

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
                raise ValueError(f"El año debe estar entre 1000 y {anio_actual}")
        return valor


class LibroRead(LibroBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    fecha_nacimiento: Optional[date] = None

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioRead(BaseModel):
    id: int
    nombre: str
    email: str
    fecha_nacimiento: Optional[date] = None
    foto_perfil: Optional[str] = None
    avatar_config: Optional[str] = None
    bio: Optional[str] = None

    model_config = {"from_attributes": True}

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    foto_perfil: Optional[str] = None
    avatar_config: Optional[str] = None
    bio: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead
