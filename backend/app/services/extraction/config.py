"""Configuración de la extracción (ACO-035).

El umbral de confianza del OCR se lee del entorno en cada llamada, como los
umbrales de ACO-023, para que la calibración y los tests lo ajusten sin
reiniciar el proceso. No es el umbral de ADR-013: mide el OCR, no la
anonimización (ADR-023:34).
"""

import os

OCR_CONFIDENCE_THRESHOLD_ENV = "ANONYMIZATION_OCR_CONFIDENCE_THRESHOLD"
PDF_TEXT_LAYER_MIN_CHARS_ENV = "ANONYMIZATION_PDF_TEXT_LAYER_MIN_CHARS"

DEFAULT_OCR_CONFIDENCE_THRESHOLD = 0.60
DEFAULT_TEXT_LAYER_MIN_CHARS = 100


class ExtractionConfigurationError(ValueError):
    """La configuración de la extracción no es válida."""


def load_ocr_threshold() -> float:
    """Devuelve el umbral de confianza del OCR vigente.

    Un valor no numérico o fuera de 0–1 impide procesar. El mensaje no incluye
    contenido del documento, solo el nombre de la variable.
    """
    value = os.environ.get(OCR_CONFIDENCE_THRESHOLD_ENV, "").strip()
    if not value:
        return DEFAULT_OCR_CONFIDENCE_THRESHOLD
    try:
        threshold = float(value)
    except ValueError:
        raise ExtractionConfigurationError(
            f"{OCR_CONFIDENCE_THRESHOLD_ENV} no es un número"
        ) from None
    if not 0.0 <= threshold <= 1.0:
        raise ExtractionConfigurationError(
            f"{OCR_CONFIDENCE_THRESHOLD_ENV} debe estar entre 0 y 1"
        )
    return threshold


def load_text_layer_min_chars() -> int:
    """Devuelve cuántos caracteres hacen falta para no pasar por OCR.

    Los 100 caracteres son un valor inicial configurable (ADR-023:51). Un
    valor que no sea un entero no negativo impide procesar; el mensaje solo
    nombra la variable, nunca el documento.
    """
    value = os.environ.get(PDF_TEXT_LAYER_MIN_CHARS_ENV, "").strip()
    if not value:
        return DEFAULT_TEXT_LAYER_MIN_CHARS
    try:
        chars = int(value)
    except ValueError:
        raise ExtractionConfigurationError(
            f"{PDF_TEXT_LAYER_MIN_CHARS_ENV} no es un número entero"
        ) from None
    if chars < 0:
        raise ExtractionConfigurationError(
            f"{PDF_TEXT_LAYER_MIN_CHARS_ENV} no puede ser negativo"
        )
    return chars
