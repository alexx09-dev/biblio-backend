# database.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

print("=== VARIABLES DE ENTORNO ===")
print(f"DB_USER desde os.environ: {os.environ.get('DB_USER', 'NO ENCONTRADO')}")
print(f"DB_HOST desde os.environ: {os.environ.get('DB_HOST', 'NO ENCONTRADO')}")
print(f"DB_PORT desde os.environ: {os.environ.get('DB_PORT', 'NO ENCONTRADO')}")
print(f"DB_NAME desde os.environ: {os.environ.get('DB_NAME', 'NO ENCONTRADO')}")
print(f"DATABASE_URL construida: {settings.DATABASE_URL}")
print("============================")

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"ssl_disabled": True},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass

# Importamos los modelos DESPUÉS de definir Base
# para que SQLAlchemy los registre antes de crear las tablas
from models.libro import Libro
from models.usuario import Usuario

# Crea todas las tablas en la BD si no existen
# Lee todos los modelos importados arriba y genera sus tablas
Base.metadata.create_all(bind=engine)

def get_db():
    # Abre una sesión de base de datos
    db = SessionLocal()
    try:
        yield db      # La entrega al endpoint que la pidió
    finally:
        db.close()    # La cierra siempre, haya error o no

if __name__ == "__main__":
    print(f"Conectando a: {settings.DATABASE_URL}")
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        print("✅ Conexión a MySQL exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")