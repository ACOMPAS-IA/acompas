from enum import Enum

from pydantic import BaseModel, Field


class AnonymizationStatus(str, Enum):
    VALIDADO = "validado"
    RETENIDO = "retenido"
    ILEGIBLE = "ilegible"


REASON_LOW_CONFIDENCE = "baja_confianza"
REASON_EMPTY_TEXT = "texto_vacio"


class AnonymizationRequest(BaseModel):
    text: str = Field(min_length=1)


class AnonymizationResult(BaseModel):
    status: AnonymizationStatus = AnonymizationStatus.VALIDADO
    confidence: float | None = None
    anonymized_text: str | None = None
    entities_count: dict[str, int] = Field(default_factory=dict)
    reason: str | None = None
