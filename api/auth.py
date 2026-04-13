# api/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import UsuarioCreate, UsuarioLogin, UsuarioRead, UsuarioUpdate, TokenResponse, UsuarioStats
from services.auth_service import (
    registrar_usuario,
    login_usuario,
    crear_token,
    obtener_usuario_actual,
)
from models.usuario import Usuario
from models.libro import Libro

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(datos: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = registrar_usuario(db, datos)
    token = crear_token({"sub": usuario.id})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}

@router.post("/login", response_model=TokenResponse)
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = login_usuario(db, datos.email, datos.password)
    token = crear_token({"sub": usuario.id})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}

@router.get("/me", response_model=UsuarioRead)
def perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

@router.put("/me", response_model=UsuarioRead)
def actualizar_perfil(
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    if datos.nombre is not None:
        usuario_actual.nombre = datos.nombre
    if datos.foto_perfil is not None:
        usuario_actual.foto_perfil = datos.foto_perfil
    if datos.avatar_config is not None:
        usuario_actual.avatar_config = datos.avatar_config
    if datos.bio is not None:
        usuario_actual.bio = datos.bio
    db.commit()
    db.refresh(usuario_actual)
    return usuario_actual

@router.get("/me/stats", response_model=UsuarioStats)
def obtener_stats(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    libros = db.query(Libro).filter(Libro.usuario_id == usuario_actual.id).all()
    total = len(libros)
    rating_promedio = round(
        sum(l.rating for l in libros) / total, 1
    ) if total > 0 else 0.0
    generos_unicos = len(set(l.genero for l in libros if l.genero))
    autores_unicos = len(set(l.autor  for l in libros if l.autor))
    return UsuarioStats(
        total_libros=total,
        rating_promedio=rating_promedio,
        generos_unicos=generos_unicos,
        autores_unicos=autores_unicos,
    )