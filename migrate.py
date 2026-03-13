# migrate.py
import subprocess
import sys
import time
from sqlalchemy import text
from database import engine
from config import settings


def esperar_base_de_datos(max_intentos=10, espera=5):
    print("\n⏳ Esperando conexión a la base de datos...")
    for intento in range(1, max_intentos + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a la base de datos")
            return
        except Exception:
            print(f"   Intento {intento}/{max_intentos} fallido — reintentando en {espera}s...")
            time.sleep(espera)
    print("❌ No se pudo conectar a la base de datos")
    sys.exit(1)


def ejecutar_comando(comando: list[str], descripcion: str):
    print(f"\n▶️  {descripcion}...")
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.stdout:
        print(resultado.stdout)
    if resultado.stderr:
        print(resultado.stderr)
    if resultado.returncode != 0:
        print(f"❌ Error al ejecutar: {' '.join(comando)}")
        sys.exit(1)
    print(f"✅ {descripcion} completado")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO PROCESO DE MIGRACIÓN")
    print(f"   Base de datos: {settings.DATABASE_URL}")
    print("=" * 60)

    # Paso 1: Esperar a que MySQL esté listo
    esperar_base_de_datos()

    # Paso 2: Aplicar migraciones existentes
    ejecutar_comando(
        ["alembic", "upgrade", "head"],
        "Aplicando migraciones a la base de datos",
    )

    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)