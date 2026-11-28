"""Fixtures de las pruebas del esquema (ACO-038).

Cada test recibe una base propia: se crea desde `template0` en el servidor de
`DATABASE_URL`, se migra con Alembic y se borra al terminar. Así los tests no
comparten estado ni dependen del orden de ejecución.

Sin `DATABASE_URL` los tests se saltan: el resto de la suite no necesita
PostgreSQL y sigue corriendo sin él. En la CI el job `backend` la define
(AC-07).

Datos sintéticos, sin red y sin modelos de lenguaje (ADR-008).
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine

BACKEND = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND / "alembic.ini"


def _base_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        pytest.skip(
            "DATABASE_URL no está definida: los tests del esquema necesitan "
            "PostgreSQL con pgvector (docker compose up -d postgres)"
        )
    return url


def _admin_engine(url: sa.URL) -> Engine:
    return sa.create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )


@pytest.fixture
def database_url() -> Iterator[str]:
    """Base vacía propia del test, creada y borrada en el servidor de la CI."""
    base = sa.engine.make_url(_base_url())
    name = f"acompas_test_{uuid.uuid4().hex[:12]}"
    admin = _admin_engine(base)
    try:
        with admin.connect() as connection:
            connection.execute(sa.text(f'CREATE DATABASE "{name}" TEMPLATE template0'))
        yield base.set(database=name).render_as_string(hide_password=False)
    finally:
        with admin.connect() as connection:
            connection.execute(
                sa.text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
            )
        admin.dispose()


@pytest.fixture
def migrated(database_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """Aplica `upgrade head` sobre la base del test y deja la URL en el entorno."""
    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(Config(str(ALEMBIC_INI)), "head")
    yield database_url


@pytest.fixture
def engine(migrated: str) -> Iterator[Engine]:
    engine = sa.create_engine(migrated)
    try:
        yield engine
    finally:
        engine.dispose()
