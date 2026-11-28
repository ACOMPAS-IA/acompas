"""Capa de datos (ACO-038).

`Base` y los modelos viven en `app.db.models`; `session` no se importa aquí
para que importar el paquete no exija `DATABASE_URL`.
"""

from __future__ import annotations

from app.db.base import Base

__all__ = ["Base"]
