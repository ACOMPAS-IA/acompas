"""Extracción de texto de un documento (ACO-035).

Recorre la ruta que fija la ficha, sección 8: tamaño, formato por firma, capa
de texto o rasterizado, OCR y confianza de documento. El tope y el límite de
páginas rechazan la petición sin procesar el resto. El módulo no registra
nada y no conserva el original.
"""

import io
import logging

import pypdfium2 as pdfium
import pytesseract
from PIL import Image

from ..anonymization.models import (
    MAX_TEXT_CHARS,
    REASON_EMPTY_TEXT,
    REASON_LOW_OCR_CONFIDENCE,
)
from .config import load_ocr_threshold, load_text_layer_min_chars
from .formats import DocumentFormat, detect_format
from .models import (
    ExtractionResult,
    FileTooLargeError,
    TextTooLongError,
)
from .ocr import ocr_image
from .pdf import RENDER_DPI, open_pdf, page_text, render_page

# Límites de la ficha, sección 8. El tope de caracteres es el del contrato de
# anonimización (ACO-024) y aquí no se amplía (ADR-023:49).
MAX_UPLOAD_BYTES = 20_000_000
MAX_PAGES = 30
MAX_IMAGE_PIXELS = 50_000_000

# Pillow no registra el EXIF al abrir un JPEG, pero sí escribe los metadatos de
# PNG y TIFF a nivel DEBUG, y una foto puede llevar geolocalización. Se sube el
# nivel de su logger para que ningún metadato pueda acabar en la traza
# (ADR-023:47, R-04); no toca otros loggers.
logging.getLogger("PIL").setLevel(logging.INFO)


class DocumentExtractor:
    """Extrae el texto de un fichero y decide si es ilegible.

    El OCR y la lectura de los umbrales se inyectan para que los tests no
    carguen Tesseract ni dependan del entorno.
    """

    def __init__(
        self,
        ocr=ocr_image,
        threshold_loader=load_ocr_threshold,
        text_layer_loader=load_text_layer_min_chars,
    ):
        self._ocr = ocr
        self._threshold_loader = threshold_loader
        self._text_layer_loader = text_layer_loader

    def extract(self, data: bytes) -> ExtractionResult:
        if len(data) > MAX_UPLOAD_BYTES:
            raise FileTooLargeError("el fichero pasa del tamaño máximo")

        threshold = self._threshold_loader()
        document_format = detect_format(data)

        if document_format is DocumentFormat.PDF:
            text, confidence = self._extract_pdf(data)
        else:
            text, confidence = self._extract_image(data)

        if not text.strip():
            return ExtractionResult(
                text="", ocr_confidence=confidence, reason=REASON_EMPTY_TEXT
            )
        if confidence is not None and confidence < threshold:
            return ExtractionResult(
                text=text,
                ocr_confidence=confidence,
                reason=REASON_LOW_OCR_CONFIDENCE,
            )
        return ExtractionResult(text=text, ocr_confidence=confidence)

    def _extract_pdf(self, data: bytes) -> tuple[str, float | None]:
        try:
            document = open_pdf(data)
        except (pdfium.PdfiumError, OSError, ValueError):
            # Cifrado o corrupto: no hay texto extraído (ADR-023:48).
            return "", None

        try:
            return self._read_pdf(document)
        except TextTooLongError:
            raise
        except (pdfium.PdfiumError, OSError, ValueError):
            return "", None
        finally:
            document.close()

    def _read_pdf(self, document) -> tuple[str, float | None]:
        pages = len(document)
        if pages > MAX_PAGES:
            raise TextTooLongError("el documento pasa del límite de páginas")

        min_chars = self._text_layer_loader()
        scale = RENDER_DPI / 72
        chunks: list[str] = []
        total = 0
        weighted = 0.0
        weight = 0

        for index in range(pages):
            page = document[index]
            layer = page_text(page)
            if len(layer.strip()) >= min_chars:
                chunk = layer
            else:
                width, height = page.get_size()
                if width * scale * height * scale > MAX_IMAGE_PIXELS:
                    # Una página desproporcionada agotaría la memoria al
                    # rasterizarla: se trata como documento ilegible sin
                    # llegar a dibujarla (mismo límite que JPG y PNG).
                    return "", None
                result = self._ocr(render_page(page))
                chunk = result.text
                if result.confidence is not None and result.weight:
                    weighted += result.confidence * result.weight
                    weight += result.weight

            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_TEXT_CHARS:
                # Se rechaza sin rasterizar el resto de páginas.
                raise TextTooLongError("el texto pasa del tope de caracteres")

        confidence = weighted / weight if weight else None
        return "\n".join(chunks), confidence

    def _extract_image(self, data: bytes) -> tuple[str, float | None]:
        try:
            image = Image.open(io.BytesIO(data))
        except (OSError, ValueError):
            return "", None

        if image.width * image.height > MAX_IMAGE_PIXELS:
            # No se decodifica: sin texto extraído, el documento es ilegible.
            return "", None

        try:
            result = self._ocr(_without_metadata(image))
        except pytesseract.TesseractNotFoundError:
            # Sin Tesseract no es un documento ilegible: es una instalación
            # rota, y el endpoint responde 500 en vez de disfrazarlo.
            raise
        except (OSError, ValueError):
            return "", None
        return result.text, result.confidence


# Metadatos que no se leen ni se propagan al OCR ni a sus temporales
# (ADR-023:47). El EXIF de una foto puede llevar geolocalización y fecha.
METADATA_KEYS = (
    "exif",
    "icc_profile",
    "dpi",
    "jfif",
    "jfif_density",
    "jfif_unit",
    "jfif_version",
    "adobe",
    "adobe_transform",
)


def _without_metadata(image: Image.Image) -> Image.Image:
    """Copia la imagen en escala de grises y sin metadatos."""
    clean = image.convert("L")
    for key in METADATA_KEYS:
        clean.info.pop(key, None)
    return clean


def extract_document(data: bytes) -> ExtractionResult:
    """Extrae el texto con la configuración del entorno."""
    return DocumentExtractor().extract(data)
