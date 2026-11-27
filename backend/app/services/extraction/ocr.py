"""OCR local con Tesseract (ACO-035).

Devuelve el texto reconstruido por líneas y la confianza de la página. La
confianza se pondera por longitud, descarta las palabras de un solo carácter y
las que Tesseract marca con −1, y cuenta todas las palabras si no hay ninguna
de más de un carácter (ADR-023:34).
"""

from dataclasses import dataclass

import pytesseract
from pytesseract import Output

LANGUAGE = "spa"


@dataclass(frozen=True)
class OcrResult:
    """Texto de una imagen y su confianza.

    `weight` es el número de caracteres que pesan en la confianza, para poder
    agregar varias páginas sin promediar medias.
    """

    text: str
    confidence: float | None
    weight: int


def ocr_image(image) -> OcrResult:
    """Reconoce el texto de una imagen PIL y calcula su confianza."""
    data = pytesseract.image_to_data(image, lang=LANGUAGE, output_type=Output.DICT)

    lines: dict[tuple[int, int, int], list[str]] = {}
    weighted = 0.0
    weight = 0
    # Reserva para una página que solo devuelve letras sueltas: sin ella se
    # quedaría sin confianza y pasaría como legible (ADR-023:34).
    single_weighted = 0.0
    single_weight = 0

    for index, word in enumerate(data["text"]):
        text = (word or "").strip()
        if not text:
            continue
        key = (
            data["block_num"][index],
            data["par_num"][index],
            data["line_num"][index],
        )
        lines.setdefault(key, []).append(text)

        try:
            confidence = float(data["conf"][index])
        except (TypeError, ValueError):
            confidence = -1.0
        if confidence < 0:
            continue
        if len(text) > 1:
            weighted += confidence * len(text)
            weight += len(text)
        else:
            single_weighted += confidence
            single_weight += 1

    if not weight:
        weighted, weight = single_weighted, single_weight

    ordered = "\n".join(" ".join(words) for _, words in sorted(lines.items()))
    mean = weighted / weight / 100 if weight else None
    return OcrResult(text=ordered, confidence=mean, weight=weight)
