# api/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import UsuarioCreate, UsuarioLogin, UsuarioRead, UsuarioUpdate, TokenResponse
from services.auth_service import (
    registrar_usuario,   # Función que crea el usuario en la BD
    login_usuario,       # Función que verifica email y password
    crear_token,         # Función que genera el JWT
    obtener_usuario_actual,  # Función que lee el token y devuelve el usuario
)
from models.usuario import Usuario

router = APIRouter(
    prefix="/api/auth",  # Todos los endpoints de este router empiezan con /api/auth
    tags=["Auth"],       # Agrupa los endpoints en el Swagger bajo la etiqueta "Auth"
)

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Crea el usuario en la BD
    # 2. Genera el token con el id del usuario como "sub"
    # 3. Devuelve el token + datos del usuario juntos
    usuario = registrar_usuario(db, datos)
    token = crear_token({"sub": usuario.id})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}

@router.post("/login", response_model=TokenResponse)
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    # 1. Verifica que el email y password sean correctos
    # 2. Genera un token nuevo
    # 3. Devuelve el token + datos del usuario
    usuario = login_usuario(db, datos.email, datos.password)
    token = crear_token({"sub": usuario.id})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}

@router.get("/me", response_model=UsuarioRead)
def perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    # Lee el token del header, busca el usuario en la BD y lo devuelve
    # No necesita body — toda la info viene del token
    return usuario_actual

@router.put("/me", response_model=UsuarioRead)
def actualizar_perfil(
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),  # Verifica que esté logueado
):
    # Solo actualiza los campos que vinieron en el body
    # Los que vinieron como None se ignoran — no se tocan en la BD
    if datos.nombre is not None:
        usuario_actual.nombre = datos.nombre
    if datos.foto_perfil is not None:
        usuario_actual.foto_perfil = datos.foto_perfil
    if datos.avatar_config is not None:
        usuario_actual.avatar_config = datos.avatar_config
    if datos.bio is not None:
        usuario_actual.bio = datos.bio
    db.commit()          # Guarda los cambios en la BD
    db.refresh(usuario_actual)  # Recarga el objeto actualizado
    return usuario_actual