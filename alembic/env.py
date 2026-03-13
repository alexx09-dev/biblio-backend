# alembic/env.py
# Configuración del entorno de migraciones Alembic
# Este archivo le dice a Alembic cómo conectarse a la BD y qué modelos observar

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Importamos Base y los modelos para que Alembic pueda detectar
# los cambios en el esquema automáticamente (autogenerate)
# Sin estos imports, Alembic no sabe qué tablas debe crear o modificar
# ---------------------------------------------------------------------------
from database import Base
from models.libro import Libro  # noqa: F401 — import necesario para el metadata

# Configuración de logging definida en alembic.ini
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# target_metadata le indica a Alembic qué modelos comparar contra la BD
# Si está en None, Alembic no puede autogenerar migraciones
# ---------------------------------------------------------------------------
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Ejecuta migraciones en modo offline (sin conexión activa a la BD).
    Genera el SQL pero no lo ejecuta — útil para revisar antes de aplicar.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecuta migraciones en modo online (con conexión activa a la BD).
    Es el modo que usamos normalmente con migrate.py
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# Determina automáticamente si ejecutar en modo online u offline
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()