"""Configuración de los umbrales de anonimización (ACO-023).

Se lee del entorno en cada llamada, no al importar el módulo, para que la
calibración y los tests puedan ajustar los valores sin reiniciar el proceso.
"""

import os

from pydantic import BaseModel, ConfigDict, Field, ValidationError

FINDING_THRESHOLD_ENV = "ANONYMIZATION_FINDING_THRESHOLD"
DOCUMENT_THRESHOLD_ENV = "ANONYMIZATION_DOCUMENT_THRESHOLD"

DEFAULT_FINDING_THRESHOLD = 0.35
DEFAULT_DOCUMENT_THRESHOLD = 0.85


class AnonymizationConfigurationError(ValueError):
    """La configuración de los umbrales no es válida."""


class AnonymizationSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    finding_threshold: float = Field(ge=0, le=1)
    document_threshold: float = Field(ge=0, le=1)


def _read_threshold(name: str, default: float) -> float:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        raise AnonymizationConfigurationError(f"{name} no es un número") from None


def load_settings() -> AnonymizationSettings:
    """Devuelve los umbrales vigentes.

    Un valor no numérico o fuera de 0–1 impide procesar. El mensaje no incluye
    contenido del documento, solo el nombre de la variable.
    """
    values = {
        "finding_threshold": _read_threshold(
            FINDING_THRESHOLD_ENV, DEFAULT_FINDING_THRESHOLD
        ),
        "document_threshold": _read_threshold(
            DOCUMENT_THRESHOLD_ENV, DEFAULT_DOCUMENT_THRESHOLD
        ),
    }
    if values["finding_threshold"] > values["document_threshold"]:
        # Un hallazgo descartado por ruido no podría retener el documento:
        # el documento pasaría como válido y el dato se quedaría sin anonimizar.
        raise AnonymizationConfigurationError(
            "el umbral de hallazgo no puede superar al de documento"
        )
    try:
        return AnonymizationSettings(**values)
    except ValidationError:
        # Se lanza fuera del except para no encadenar la validación.
        error = AnonymizationConfigurationError(
            "los umbrales deben estar entre 0 y 1"
        )
    raise error
