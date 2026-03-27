# services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.usuario import Usuario
from schemas import UsuarioCreate
from config import settings
from database import get_db

# ---------------------------------------------------------------------------
# Configuración del hasheador de contraseñas
# bcrypt es el algoritmo más seguro y recomendado para contraseñas
# "deprecated=auto" actualiza automáticamente hashes viejos si cambiamos algoritmo
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# Le dice a FastAPI dónde está el endpoint de login para obtener el token
# Cuando un endpoint use Depends(oauth2_scheme), FastAPI leerá el header:
# Authorization: Bearer <token>
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ---------------------------------------------------------------------------
# Contraseñas
# ---------------------------------------------------------------------------
def hashear_password(password: str) -> str:
    # Convierte "miPassword123" → "$2b$12$..." (hash irreversible)
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hash: str) -> bool:
    # Compara el password que escribió el usuario con el hash guardado en BD
    # Nunca desencripta — vuelve a hashear y compara
    return pwd_context.verify(password_plano, password_hash)

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def crear_token(data: dict) -> str:
    payload = data.copy()                  # Copiamos para no modificar el original
    expira = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expira})        # Agregamos la fecha de expiración al token
    # Firmamos el token con nuestra SECRET_KEY — solo nosotros podemos verificarlo
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decodificar_token(token: str) -> Optional[dict]:
    try:
        # Verifica la firma y que no haya expirado
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        # Si el token es falso, fue modificado o expiró → devuelve None
        return None

# ---------------------------------------------------------------------------
# Servicios
# ---------------------------------------------------------------------------
def registrar_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    # Primero verificamos que el email no esté registrado
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese email."
        )
    usuario = Usuario(
        nombre           = datos.nombre,
        email            = datos.email,
        password_hash    = hashear_password(datos.password),  # Nunca guardamos el password plano
        fecha_nacimiento = datos.fecha_nacimiento,
    )
    db.add(usuario)      # Prepara el INSERT
    db.commit()          # Ejecuta el INSERT en la BD
    db.refresh(usuario)  # Recarga el objeto con el id que asignó MySQL
    return usuario

def login_usuario(db: Session, email: str, password: str) -> Usuario:
    # Buscamos el usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    # Si no existe O la contraseña es incorrecta → mismo error (por seguridad no decimos cuál)
    if not usuario or not verificar_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos."
        )
    return usuario

def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),  # Lee el token del header Authorization
    db: Session = Depends(get_db),        # Abre una sesión de BD
) -> Usuario:
    payload = decodificar_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado."
        )
    # El "sub" del token es el id del usuario que guardamos al crear el token
    usuario_id = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado."
        )
    return usuario