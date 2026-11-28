"""Entorno de Alembic (ACO-038).

La URL sale de `DATABASE_URL` (app/db/config.py), no de `alembic.ini`.
`compare_type=True` hace que `alembic check` compare tipos y no solo tablas:
sin él, un `VARCHAR(64)` que se quedara en `VARCHAR` pasaría desapercibido.

`downgrade` no elimina la extensión `vector`: en Compose la crea
`infra/docker/postgres/init/01-init.sql` y puede haber otras tablas usándola.
La migración `0001` la crea con `IF NOT EXISTS` y no la retira al bajar.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.base import Base
from app.db.config import database_url

# Registra las 18 tablas en `Base.metadata`.
import app.db.models  # noqa: F401,E402

config = context.config

if config.config_file_name is not None:
    # `disable_existing_loggers=False`: sin él, `fileConfig` apaga los loggers
    # ya creados —los de la aplicación— y cualquier test que capture registros
    # después de una migración deja de verlos.
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse."""
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones contra la base de `DATABASE_URL`."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url()
    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
