from enum import Enum

from pydantic import BaseModel, Field

# Máximo de caracteres del contrato HTTP de anonimización (ficha ACO-024, P2).
MAX_TEXT_CHARS = 30_000


class AnonymizationStatus(str, Enum):
    VALIDADO = "validado"
    RETENIDO = "retenido"
    ILEGIBLE = "ilegible"


REASON_LOW_CONFIDENCE = "baja_confianza"
REASON_EMPTY_TEXT = "texto_vacio"


class AnonymizationRequest(BaseModel):
    # El texto vacío es válido: el servicio lo trata como documento ilegible
    # (ficha ACO-023, P10). El máximo es el del contrato HTTP (ficha ACO-024, P2).
    text: str = Field(max_length=MAX_TEXT_CHARS)


class AnonymizationResult(BaseModel):
    status: AnonymizationStatus = AnonymizationStatus.VALIDADO
    confidence: float | None = None
    anonymized_text: str | None = None
    entities_count: dict[str, int] = Field(default_factory=dict)
    reason: str | None = None
