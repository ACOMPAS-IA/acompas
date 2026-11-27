"""Extracción de texto de PDF, JPG y PNG (ACO-035).

El módulo convierte un fichero en texto y, cuando hay OCR, en una confianza de
documento. No decide la anonimización, no persiste el original y no registra
el nombre del fichero ni el texto extraído.
"""

from .config import (
    DEFAULT_OCR_CONFIDENCE_THRESHOLD,
    DEFAULT_TEXT_LAYER_MIN_CHARS,
    OCR_CONFIDENCE_THRESHOLD_ENV,
    PDF_TEXT_LAYER_MIN_CHARS_ENV,
    ExtractionConfigurationError,
    load_ocr_threshold,
    load_text_layer_min_chars,
)
from .models import (
    ExtractionError,
    ExtractionResult,
    FileTooLargeError,
    TextTooLongError,
    UnsupportedFormatError,
)
from .service import DocumentExtractor, extract_document

__all__ = [
    "DEFAULT_OCR_CONFIDENCE_THRESHOLD",
    "DEFAULT_TEXT_LAYER_MIN_CHARS",
    "DocumentExtractor",
    "ExtractionConfigurationError",
    "ExtractionError",
    "ExtractionResult",
    "FileTooLargeError",
    "OCR_CONFIDENCE_THRESHOLD_ENV",
    "PDF_TEXT_LAYER_MIN_CHARS_ENV",
    "TextTooLongError",
    "UnsupportedFormatError",
    "extract_document",
    "load_ocr_threshold",
    "load_text_layer_min_chars",
]
