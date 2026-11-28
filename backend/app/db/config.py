"""Configuración de la base de datos (ACO-038).

`DATABASE_URL` es la única fuente de la cadena de conexión y llega por entorno:
en Compose la inyecta el servicio `backend`, en la CI el job y en local el
`.env` (ADR-015 §1). No hay valor por defecto a propósito: una base equivocada
en silencio es peor que un error al arrancar.
"""

from __future__ import annotations

import os

VARIABLE = "DATABASE_URL"


def database_url() -> str:
    """Devuelve `DATABASE_URL` o falla con un mensaje que dice qué falta."""
    url = os.environ.get(VARIABLE, "").strip()
    if not url:
        raise RuntimeError(
            f"{VARIABLE} no está definida. Copia el valor de .env.example en tu "
            ".env o exporta la cadena de conexión antes de ejecutar Alembic."
        )
    return url
