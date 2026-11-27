"""Tipos de la extracción (ACO-035)."""

from dataclasses import dataclass


class ExtractionError(Exception):
    """El fichero no se puede procesar y el endpoint debe responder un error."""


class FileTooLargeError(ExtractionError):
    """El fichero pasa del tamaño máximo admitido."""


class UnsupportedFormatError(ExtractionError):
    """La firma del fichero no es PDF, JPEG ni PNG."""


class TextTooLongError(ExtractionError):
    """El texto pasa del tope de caracteres o de páginas."""


@dataclass(frozen=True)
class ExtractionResult:
    """Texto extraído y, si hubo OCR, la confianza del documento.

    `reason` es `None` cuando el documento se puede anonimizar; si no, es el
    motivo de ilegibilidad (`texto_vacio` o `baja_confianza_ocr`), que el
    endpoint devuelve sin llegar a la anonimización.
    """

    text: str
    ocr_confidence: float | None = None
    reason: str | None = None
