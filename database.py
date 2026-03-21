# database.py
# Configuración del motor de base de datos y sesiones SQLAlchemy
# La URL de conexión viene de config.py (no se hardcodea aquí)
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

# ---------------------------------------------------------------------------
# Debug temporal - ver qué variables está leyendo Render
# ---------------------------------------------------------------------------
print("=== VARIABLES DE ENTORNO ===")
print(f"DB_USER desde os.environ: {os.environ.get('DB_USER', 'NO ENCONTRADO')}")
print(f"DB_HOST desde os.environ: {os.environ.get('DB_HOST', 'NO ENCONTRADO')}")
print(f"DB_PORT desde os.environ: {os.environ.get('DB_PORT', 'NO ENCONTRADO')}")
print(f"DB_NAME desde os.environ: {os.environ.get('DB_NAME', 'NO ENCONTRADO')}")
print(f"DATABASE_URL construida: {settings.DATABASE_URL}")
print("============================")

# ---------------------------------------------------------------------------
# Motor de conexión a MySQL
# pool_pre_ping=True: verifica que la conexión esté activa antes de usarla
# Evita errores por conexiones que MySQL cerró por inactividad
# ---------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# ---------------------------------------------------------------------------
# Fábrica de sesiones
# autocommit=False → los cambios se confirman explícitamente con db.commit()
# autoflush=False  → no envía cambios a la BD hasta que se haga commit
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---------------------------------------------------------------------------
# Clase base para todos los modelos ORM del proyecto
# Cada modelo (ej: Libro) heredará de esta clase
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass

# ---------------------------------------------------------------------------
# Dependencia de FastAPI para inyectar la sesión de BD en los endpoints
# Garantiza que la sesión se cierre correctamente al terminar cada request
# ---------------------------------------------------------------------------
def get_db():
    """
    Generador que provee una sesión de BD por request.
    El bloque finally garantiza el cierre aunque ocurra una excepción.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Prueba rápida de conexión
# Ejecutar directamente: python database.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Conectando a: {settings.DATABASE_URL}")
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        print("✅ Conexión a MySQL exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
