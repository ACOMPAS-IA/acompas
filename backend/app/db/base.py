"""Base declarativa del modelo de datos (ACO-038).

Un solo `MetaData` con convención de nombres, para que las restricciones que
genera SQLAlchemy tengan nombre estable y en ASCII (ficha §7). Los nombres son
los que Alembic compara en `alembic check`.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Convención de nombres de SQLAlchemy. Solo cubre lo que el modelo declara:
# claves primarias, claves foráneas y restricciones únicas. Los índices llevan
# nombre explícito porque son parte del esquema de ADR-022 y del E/R §4.
#
# La clave foránea no lleva el nombre de la tabla referida: con él,
# `fk_solicitud_desbloqueo_credito_motivo_resolucion_motivo_resolucion` pasa de
# los 63 caracteres que PostgreSQL admite y el servidor lo truncaría en
# silencio. La columna ya identifica el destino.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base de los 18 modelos del Sprint 2."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
