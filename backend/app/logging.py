"""Configuración de logging de la aplicación (ACO-028, ADR-015 §4).

Se ejecuta una vez al arrancar o importar la aplicación, no en cada petición.
"""

import logging

LOG_LEVEL = logging.INFO

# Loggers del SDK que pueden emitir contenido de peticiones o respuestas.
# Con nivel efectivo INFO o superior, el cuerpo se queda en DEBUG y no se emite.
_SDK_LOGGERS = ("anthropic", "httpx2", "httpcore2")
_APP_LOGGER = "app"


def configure_logging() -> None:
    """Configura el registro de la aplicación y del SDK.

    No se usa ``propagate=False``: los avisos y errores del SDK deben seguir
    llegando al registro de la aplicación. La función es idempotente.
    """
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger(_APP_LOGGER).setLevel(LOG_LEVEL)
    for name in _SDK_LOGGERS:
        logging.getLogger(name).setLevel(LOG_LEVEL)
