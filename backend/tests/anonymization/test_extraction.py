"""Tests de la extracción de texto de ACO-035.

No cargan Tesseract ni el modelo: el OCR se sustituye por un doble y los
ficheros se generan en memoria. Los documentos son sintéticos (ACO-051).
"""

import io
import logging

import pytest
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.pdfencrypt import StandardEncryption
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.services.anonymization.models import (
    REASON_EMPTY_TEXT,
    REASON_LOW_OCR_CONFIDENCE,
)
from app.services.extraction import (
    DocumentExtractor,
    ExtractionConfigurationError,
    FileTooLargeError,
    TextTooLongError,
    UnsupportedFormatError,
    load_ocr_threshold,
    load_text_layer_min_chars,
)
from app.services.extraction import service as service_module
from app.services.extraction.config import OCR_CONFIDENCE_THRESHOLD_ENV
from app.services.extraction.formats import DocumentFormat, detect_format
from app.services.extraction.ocr import OcrResult
from app.services.extraction.service import (
    MAX_IMAGE_PIXELS,
    MAX_PAGES,
    MAX_UPLOAD_BYTES,
)

LONG_TEXT = "Texto de capa suficientemente largo para no pasar por OCR. " * 3


def make_pdf(pages, encrypt=None, image_page=False, pagesize=A4) -> bytes:
    """PDF de prueba: una página por elemento de `pages`.

    Cada página dibuja su texto en la capa. Con `image_page`, la página es una
    imagen: no tiene capa de texto y obliga a rasterizar.
    """
    buffer = io.BytesIO()
    options = {"pagesize": pagesize}
    if encrypt is not None:
        options["encrypt"] = encrypt
    document = canvas.Canvas(buffer, **options)
    for page in pages:
        if image_page:
            picture = Image.new("L", (600, 200), color=255)
            document.drawImage(ImageReader(picture), 60, 600, 400, 130)
        else:
            document.drawString(60, 800, page)
        document.showPage()
    document.save()
    return buffer.getvalue()


def make_image(fmt="PNG", size=(600, 200), exif=None) -> bytes:
    image = Image.new("L", size, color=255)
    buffer = io.BytesIO()
    if fmt == "JPEG":
        image = image.convert("RGB")
        if exif is not None:
            image.save(buffer, "JPEG", exif=exif)
        else:
            image.save(buffer, "JPEG")
    else:
        image.save(buffer, fmt)
    return buffer.getvalue()


class FakeOcr:
    """Doble del OCR: devuelve lo que se le diga y cuenta las llamadas."""

    def __init__(self, text="Texto reconocido", confidence=0.9, weight=16):
        self.text = text
        self.confidence = confidence
        self.weight = weight
        self.calls = 0
        self.images = []

    def __call__(self, image):
        self.calls += 1
        self.images.append(image)
        return OcrResult(
            text=self.text, confidence=self.confidence, weight=self.weight
        )


def extractor(ocr=None, threshold=0.60):
    return DocumentExtractor(ocr=ocr or FakeOcr(), threshold_loader=lambda: threshold)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"%PDF-1.7\n...", DocumentFormat.PDF),
        (b"\xff\xd8\xff\xe0\x00\x10JFIF", DocumentFormat.JPEG),
        (b"\x89PNG\r\n\x1a\n\x00\x00", DocumentFormat.PNG),
    ],
)
def test_format_is_decided_by_signature(data, expected):
    assert detect_format(data) is expected


@pytest.mark.parametrize("data", [b"", b"texto plano", b"PK\x03\x04", b"%PD"])
def test_unknown_signature_is_rejected(data):
    # Un `.txt` renombrado no es un PDF: se decide por el contenido.
    with pytest.raises(UnsupportedFormatError):
        detect_format(data)


def test_limits_are_the_ones_in_the_card():
    assert MAX_UPLOAD_BYTES == 20_000_000
    assert MAX_PAGES == 30
    assert MAX_IMAGE_PIXELS == 50_000_000


def test_oversized_file_is_rejected(monkeypatch):
    monkeypatch.setattr(service_module, "MAX_UPLOAD_BYTES", 10)

    with pytest.raises(FileTooLargeError):
        extractor().extract(b"%PDF-" + b"x" * 11)


def test_file_at_the_limit_is_not_rejected(monkeypatch):
    payload = make_pdf([LONG_TEXT])
    monkeypatch.setattr(service_module, "MAX_UPLOAD_BYTES", len(payload))

    # El límite es un máximo inclusive: se lee y se procesa.
    assert extractor().extract(payload).reason is None


def test_text_layer_is_read_without_calling_ocr():
    ocr = FakeOcr()
    result = extractor(ocr).extract(make_pdf([LONG_TEXT, LONG_TEXT]))

    assert ocr.calls == 0
    assert result.reason is None
    assert result.ocr_confidence is None
    assert result.text.count("Texto de capa") == 6


def test_page_without_text_layer_goes_through_ocr():
    ocr = FakeOcr(text="Informe reconocido")
    result = extractor(ocr).extract(make_pdf(["imagen"], image_page=True))

    assert ocr.calls == 1
    assert result.text == "Informe reconocido"
    assert result.ocr_confidence == pytest.approx(0.9)
    assert result.reason is None


def test_short_text_layer_goes_through_ocr():
    ocr = FakeOcr(text="Reconocido")
    result = extractor(ocr).extract(make_pdf(["corto"]))

    assert ocr.calls == 1
    assert result.text == "Reconocido"


def test_document_without_ocr_pages_has_no_ocr_confidence():
    result = extractor().extract(make_pdf([LONG_TEXT]))

    assert result.ocr_confidence is None


def test_mixed_pdf_takes_confidence_from_ocr_pages_only():
    # Dos páginas: la primera trae capa de texto y no pasa por OCR; la segunda
    # es una imagen y sí. La confianza del documento sale solo de la segunda.
    ocr = FakeOcr(text="Reconocido", confidence=0.5, weight=10)

    result = extractor(ocr).extract(make_mixed_pdf())

    assert ocr.calls == 1
    assert result.ocr_confidence == pytest.approx(0.5)
    assert "Texto de capa" in result.text
    assert "Reconocido" in result.text


def make_mixed_pdf() -> bytes:
    """PDF de dos páginas: capa de texto larga en la primera, imagen en la segunda."""
    buffer = io.BytesIO()
    document = canvas.Canvas(buffer, pagesize=A4)
    document.drawString(60, 800, LONG_TEXT)
    document.showPage()
    picture = Image.new("L", (600, 200), color=255)
    document.drawImage(ImageReader(picture), 60, 600, 400, 130)
    document.showPage()
    document.save()
    return buffer.getvalue()


def test_char_too_long_is_rejected_without_rendering_the_rest():
    # Primera página con más de 30.000 caracteres en la capa y una segunda que
    # necesitaría OCR: no se llega a rasterizar.
    ocr = FakeOcr()
    payload = make_pdf(["a" * 30_001], image_page=False)

    with pytest.raises(TextTooLongError):
        extractor(ocr).extract(payload)

    assert ocr.calls == 0


def test_second_page_is_not_rasterised_after_the_limit():
    ocr = FakeOcr()
    payload = make_pdf_with_image_page()

    with pytest.raises(TextTooLongError):
        extractor(ocr).extract(payload)

    assert ocr.calls == 0


def make_pdf_with_image_page() -> bytes:
    """PDF de dos páginas: texto largo en la primera, imagen en la segunda."""
    buffer = io.BytesIO()
    document = canvas.Canvas(buffer, pagesize=A4)
    document.drawString(60, 800, "a" * 30_001)
    document.showPage()
    picture = Image.new("L", (600, 200), color=255)
    document.drawImage(ImageReader(picture), 60, 600, 400, 130)
    document.showPage()
    document.save()
    return buffer.getvalue()


def test_page_limit_is_rejected_before_rasterising():
    ocr = FakeOcr()
    payload = make_pdf([""] * (MAX_PAGES + 1))

    with pytest.raises(TextTooLongError):
        extractor(ocr).extract(payload)

    assert ocr.calls == 0


@pytest.mark.parametrize(
    "payload",
    [
        b"%PDF-1.4\nbasura",
        b"%PDF-1.4\n" + b"\x00" * 200,
    ],
)
def test_corrupt_pdf_is_illegible(payload):
    result = extractor().extract(payload)

    assert result.text == ""
    assert result.reason == REASON_EMPTY_TEXT


def test_encrypted_pdf_is_illegible():
    payload = make_pdf([LONG_TEXT], encrypt=StandardEncryption("secreto"))

    result = extractor().extract(payload)

    assert result.reason == REASON_EMPTY_TEXT


def test_image_without_text_is_illegible():
    ocr = FakeOcr(text="   ", confidence=0.1, weight=0)

    result = extractor(ocr).extract(make_image())

    assert result.reason == REASON_EMPTY_TEXT
    assert result.text == ""


def test_low_ocr_confidence_is_illegible_but_keeps_the_text():
    ocr = FakeOcr(text="Texto dudoso", confidence=0.42, weight=20)

    result = extractor(ocr).extract(make_image())

    assert result.reason == REASON_LOW_OCR_CONFIDENCE
    assert result.text == "Texto dudoso"
    assert result.ocr_confidence == pytest.approx(0.42)


def test_png_and_jpeg_go_through_ocr():
    ocr = FakeOcr(text="Reconocido")

    assert extractor(ocr).extract(make_image("PNG")).text == "Reconocido"
    assert extractor(ocr).extract(make_image("JPEG")).text == "Reconocido"
    assert ocr.calls == 2


def test_image_over_the_pixel_limit_is_not_decoded(monkeypatch):
    ocr = FakeOcr()
    monkeypatch.setattr(service_module, "MAX_IMAGE_PIXELS", 100)

    result = extractor(ocr).extract(make_image(size=(600, 200)))

    assert result.reason == REASON_EMPTY_TEXT
    assert ocr.calls == 0


def test_pdf_page_over_the_pixel_limit_is_not_rasterised(monkeypatch):
    # Una página con un tamaño desproporcionado agotaría la memoria a 300 ppp:
    # se trata como ilegible antes de dibujarla, con el mismo límite que una
    # imagen.
    ocr = FakeOcr()
    monkeypatch.setattr(service_module, "MAX_IMAGE_PIXELS", 100)

    result = extractor(ocr).extract(make_pdf(["corto"], pagesize=(2000, 2000)))

    assert result.reason == REASON_EMPTY_TEXT
    assert ocr.calls == 0


def test_missing_tesseract_is_not_disguised_as_illegible():
    # Si falta el binario, la petición falla (500) en vez de devolver
    # «ilegible» y esconder una instalación rota.
    import pytesseract

    def broken(image):
        raise pytesseract.TesseractNotFoundError()

    with pytest.raises(pytesseract.TesseractNotFoundError):
        DocumentExtractor(ocr=broken).extract(make_image())


def test_exif_is_not_read_nor_passed_to_the_ocr(caplog):
    exif = Image.Exif()
    exif[0x010F] = "ACOMPAS-MARCA-EXIF"
    payload = make_image("JPEG", exif=exif)
    ocr = FakeOcr(text="Reconocido")
    caplog.set_level(logging.DEBUG)

    result = extractor(ocr).extract(payload)

    assert ocr.calls == 1
    assert "exif" not in ocr.images[0].info
    assert "ACOMPAS-MARCA-EXIF" not in repr(result)
    assert "ACOMPAS-MARCA-EXIF" not in caplog.text


# Imagen pequeña para los tests de confianza: no hace falta OCR real.
def fake_tesseract_data(monkeypatch, words):
    """Sustituye `pytesseract.image_to_data` por una tabla fija."""

    def image_to_data(image, lang=None, output_type=None):
        return {
            "text": [word for word, _, _, _ in words],
            "conf": [str(conf) for _, conf, _, _ in words],
            "block_num": [block for _, _, block, _ in words],
            "par_num": [paragraph for _, _, _, paragraph in words],
            "line_num": [paragraph for _, _, _, paragraph in words],
        }

    monkeypatch.setattr("pytesseract.image_to_data", image_to_data)


def test_ocr_confidence_is_weighted_by_length_and_skips_one_char_words(
    monkeypatch,
):
    from app.services.extraction.ocr import ocr_image

    fake_tesseract_data(
        monkeypatch,
        [
            ("Paciente", 90.0, 1, 1),
            ("a", 10.0, 1, 1),  # una sola letra: no pesa
            ("Rosario", 60.0, 1, 1),
            ("ruido", -1.0, 1, 1),  # sin confianza: no pesa
        ],
    )

    result = ocr_image(Image.new("L", (10, 10)))

    # (90*8 + 60*7) / (8 + 7) / 100
    assert result.confidence == pytest.approx((90 * 8 + 60 * 7) / 15 / 100)
    assert result.weight == 15


def test_ocr_confidence_falls_back_to_one_char_words(monkeypatch):
    # ADR-023:34: si no hay ninguna palabra de más de un carácter, se cuentan
    # todas. Si no, una página que solo devuelve letras sueltas se quedaría sin
    # confianza y pasaría como legible.
    from app.services.extraction.ocr import ocr_image

    fake_tesseract_data(
        monkeypatch,
        [
            ("a", 90.0, 1, 1),
            ("b", 60.0, 1, 1),
        ],
    )

    result = ocr_image(Image.new("L", (10, 10)))

    assert result.confidence == pytest.approx((90 + 60) / 2 / 100)
    assert result.weight == 2


def test_ocr_reconstructs_lines_without_markers(monkeypatch):
    from app.services.extraction.ocr import ocr_image

    fake_tesseract_data(
        monkeypatch,
        [
            ("Paciente:", 90.0, 1, 1),
            ("Rosario", 90.0, 1, 1),
            ("DNI:", 90.0, 1, 2),
            ("12345678Z", 90.0, 1, 2),
        ],
    )

    result = ocr_image(Image.new("L", (10, 10)))

    assert result.text == "Paciente: Rosario\nDNI: 12345678Z"


def test_ocr_without_words_has_no_confidence(monkeypatch):
    from app.services.extraction.ocr import ocr_image

    fake_tesseract_data(monkeypatch, [("", -1.0, 1, 1)])

    result = ocr_image(Image.new("L", (10, 10)))

    assert result.text == ""
    assert result.confidence is None
    assert result.weight == 0


def test_the_module_does_not_log_anything():
    # AC-10 y R-04: el módulo de extracción no registra el nombre del fichero,
    # el texto extraído ni el del OCR. La única llamada al registro es subir el
    # nivel del logger de Pillow, que no escribe nada.
    import ast
    from pathlib import Path

    package = Path(service_module.__file__).parent
    forbidden = {"debug", "info", "warning", "error", "critical", "exception"}
    offenders = []

    for path in sorted(package.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in forbidden
            ):
                offenders.append(f"{path.name}:{node.lineno}:{node.func.attr}")

    assert offenders == []


@pytest.mark.parametrize("value", ["abc", "1.5", "-0.1"])
def test_invalid_ocr_threshold_is_reported(monkeypatch, value):
    monkeypatch.setenv(OCR_CONFIDENCE_THRESHOLD_ENV, value)

    with pytest.raises(ExtractionConfigurationError):
        load_ocr_threshold()


def test_threshold_ignores_surrounding_spaces(monkeypatch):
    monkeypatch.setenv(OCR_CONFIDENCE_THRESHOLD_ENV, " 0.60 ")

    assert load_ocr_threshold() == pytest.approx(0.60)


def test_default_threshold_is_060(monkeypatch):
    monkeypatch.delenv(OCR_CONFIDENCE_THRESHOLD_ENV, raising=False)

    assert load_ocr_threshold() == pytest.approx(0.60)


def test_threshold_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv(OCR_CONFIDENCE_THRESHOLD_ENV, "0.30")
    ocr = FakeOcr(text="Texto dudoso", confidence=0.42, weight=10)

    # Con el umbral por defecto sería ilegible; con 0.30 pasa.
    assert DocumentExtractor(ocr=ocr).extract(make_image()).reason is None
    assert extractor(ocr).extract(make_image()).reason == REASON_LOW_OCR_CONFIDENCE


def test_text_layer_threshold_comes_from_the_environment(monkeypatch):
    # Los 100 caracteres son configurables (ADR-023:51): con 5, una capa de
    # seis caracteres ya se lee sin OCR.
    monkeypatch.setenv("ANONYMIZATION_PDF_TEXT_LAYER_MIN_CHARS", "5")
    ocr = FakeOcr(text="Reconocido")

    result = DocumentExtractor(ocr=ocr).extract(make_pdf(["abcdef"]))

    assert ocr.calls == 0
    assert "abcdef" in result.text


def test_default_text_layer_threshold_is_100(monkeypatch):
    monkeypatch.delenv("ANONYMIZATION_PDF_TEXT_LAYER_MIN_CHARS", raising=False)

    assert load_text_layer_min_chars() == 100


@pytest.mark.parametrize("value", ["abc", "1.5", "-1"])
def test_invalid_text_layer_threshold_is_reported(monkeypatch, value):
    monkeypatch.setenv("ANONYMIZATION_PDF_TEXT_LAYER_MIN_CHARS", value)

    with pytest.raises(ExtractionConfigurationError):
        load_text_layer_min_chars()
