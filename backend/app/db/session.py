"""Motor y sesiones de SQLAlchemy (ACO-038).

Se construyen al pedirlos, no al importar: importar `app.main` no debe exigir
una base de datos. ACO-043 y posteriores usarán `session_scope`; aquí solo se
deja el punto de entrada, sin repositorios (ficha §5).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.config import database_url

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Motor único del proceso, creado la primera vez que se pide."""
    global _engine
    if _engine is None:
        _engine = create_engine(database_url(), pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _session_factory


@contextmanager
def session_scope() -> Iterator[Session]:
    """Sesión con transacción: confirma si el bloque termina bien."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def dispose_engine() -> None:
    """Cierra el motor. Lo usan los tests y el apagado del proceso."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
