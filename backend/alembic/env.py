from logging.config import fileConfig
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Rutas del proyecto ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "app"))

# Importa Base y modelos
from app.core.config import settings
from app.core.database import Base  # Base.metadata
from app import models  # noqa: F401  # efectos secundarios

# --- Config de Alembic ---
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Lee argumento opcional -x db_url
x_args = context.get_x_argument(as_dictionary=True)
forced_url = x_args.get("db_url")

# Construye URL: usa forced_url si viene en -x, si no la de settings
default_url = settings.DATABASE_URL.replace("asyncpg", "psycopg2")
sqlalchemy_url = forced_url or default_url
config.set_main_option("sqlalchemy.url", sqlalchemy_url)


def run_migrations_offline() -> None:
    """Modo offline: genera SQL sin conectarse a la BD."""
    context.configure(
        url=sqlalchemy_url,
        target_metadata=Base.metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online: se conecta a la BD y aplica migraciones."""
    connectable = engine_from_config(
        {"sqlalchemy.url": sqlalchemy_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
