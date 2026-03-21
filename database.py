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

from models.libro import Libro          # ← AGREGADO
Base.metadata.create_all(bind=engine)  # ← AGREGADO

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Conectando a: {settings.DATABASE_URL}")
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        print("✅ Conexión a MySQL exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
