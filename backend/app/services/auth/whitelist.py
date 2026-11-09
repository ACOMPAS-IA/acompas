"""Lista blanca del piloto (ACO-015; ADR-017 D1-A y D4).

La lista vive en el entorno, no en la base de datos: es una excepción temporal
a ADR-009 limitada a local y demo. Se lee en cada petición, como la
configuración de ACO-014, para que el proceso no dependa de un valor capturado
al importar el módulo.
"""

import logging
import os
from collections.abc import Collection

EMAILS_AUTORIZADOS_ENV = "EMAILS_AUTORIZADOS"

logger = logging.getLogger(__name__)


def parse_authorized_emails(raw: str | None) -> frozenset[str]:
    """Normaliza una lista separada por comas.

    Se aplica ``trim`` y minúsculas a cada dirección y se descartan las
    entradas vacías. No hay comodines ni patrones de dominio: la comparación
    posterior es exacta.
    """
    if not raw:
        return frozenset()

    emails = set()
    for item in raw.split(","):
        email = item.strip().lower()
        if email:
            emails.add(email)
    return frozenset(emails)


def load_authorized_emails() -> frozenset[str]:
    """Devuelve la lista vigente.

    Ausente o vacía equivale a lista vacía: el backend sigue en marcha y
    rechaza a todos (cierre por defecto).
    """
    return parse_authorized_emails(os.environ.get(EMAILS_AUTORIZADOS_ENV))


def is_email_authorized(email: str | None, authorized: Collection[str]) -> bool:
    """Comprueba un email contra una lista ya normalizada.

    Un email ausente o vacío nunca está autorizado. ``*`` es un carácter
    literal y solo coincide con otro ``*``.
    """
    if not email:
        return False

    normalized = email.strip().lower()
    return bool(normalized) and normalized in authorized


def log_whitelist_summary() -> None:
    """Registra el tamaño de la lista al arrancar, nunca sus valores."""
    emails = load_authorized_emails()
    if emails:
        logger.info(
            "Lista blanca del piloto: %d direcciones autorizadas", len(emails)
        )
    else:
        logger.error(
            "Lista blanca del piloto ausente o vacía: 0 direcciones autorizadas; "
            "se rechazará a todos con 403"
        )
