"""Calibración y privacidad sobre los renders sintéticos (ACO-035).

Estos tests necesitan OCR real y se saltan si faltan el binario de Tesseract o
el paquete de español. La medición que cuenta es la de la PR, hecha sobre la
imagen construida en frío (ADR-023:25); aquí se comprueba que no haya
regresiones gruesas y que ninguna entidad garantizada sobreviva.
"""

import re
import tempfile
import time
import unicodedata
from pathlib import Path

import pypdfium2 as pdfium
import pytest

from app.services.anonymization import AnonymizationService
from app.services.anonymization.analyzer import build_analyzer
from app.services.anonymization.models import AnonymizationStatus
from app.services.extraction import DocumentExtractor
from app.services.extraction.ocr import LANGUAGE
from tests.anonymization.test_service import (
    IDENTIFIER_CATEGORIES,
    assert_manifest_entity_absent,
    guaranteed_manifest_entities,
    manifest_entities,
)
from tests.synthetic_data import load_document

RENDERS = Path(__file__).resolve().parent / "renders"
DOCUMENTS = ("informe_patologia_01", "analitica_01", "carta_oncologia_01")
OCR_SUFFIXES = ("escaneo.pdf", "foto.jpg")
LAYER_SUFFIX = "capa.pdf"

# Umbrales de ADR-023:27-31.
MAX_GLOBAL_CER = 0.10
MAX_IDENTIFIER_CER = 0.02
# Tope amplio: el criterio fino es ≤3 s por página, pero medirlo en la CI da
# falsos positivos y la medición que cuenta es la de la imagen, en frío. Aquí
# solo se vigila que no haya una regresión gruesa, y por eso el tope es tres
# veces lo medido.
MAX_SECONDS_PER_PAGE = 10.0


def ocr_available() -> tuple[bool, str]:
    """Comprueba binario y paquete de idioma sin cargar nada más."""
    try:
        import pytesseract
    except Exception as error:  # pragma: no cover - depende del entorno
        return False, f"pytesseract no importable: {error}"

    try:
        languages = pytesseract.get_languages(config="")
    except Exception as error:  # pragma: no cover - depende del entorno
        return False, f"tesseract no disponible: {error}"

    if LANGUAGE not in languages:
        return False, f"falta el paquete de idioma {LANGUAGE}"
    return True, ""


available, reason = ocr_available()
requires_ocr = pytest.mark.skipif(not available, reason=reason)


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def edit_distance(reference: str, hypothesis: str) -> int:
    """Distancia de Levenshtein entre dos cadenas."""
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for row, character in enumerate(reference, 1):
        current = [row]
        for column, other in enumerate(hypothesis, 1):
            current.append(
                min(
                    previous[column] + 1,
                    current[column - 1] + 1,
                    previous[column - 1] + (character != other),
                )
            )
        previous = current
    return previous[-1]


def cer(reference: str, hypothesis: str) -> float:
    expected = normalise(reference)
    if not expected:
        return 0.0 if not normalise(hypothesis) else 1.0
    return edit_distance(expected, normalise(hypothesis)) / len(expected)


def identifier_values(document_name: str) -> list[str]:
    """Identificativos del manifiesto de ACO-051 para ese documento."""
    values = [
        entity["text"]
        for entity in manifest_entities(document_name)
        if entity["category"] in IDENTIFIER_CATEGORIES
    ]
    assert values
    return values


def identifier_cer(document_name: str, hypothesis: str) -> float:
    """CER de los identificativos.

    Se busca cada identificativo en el texto del OCR —por su principio o su
    final, sin espacios— y se mide la distancia en la ventana que lo rodea. Si
    no aparece ninguno de los dos extremos, el identificativo cuenta como
    perdido entero. Mide lo que importa: que el DNI o el número de historia
    lleguen intactos.
    """
    compact = normalise(hypothesis).replace(" ", "")
    total_distance = 0
    total_length = 0

    for value in identifier_values(document_name):
        expected = normalise(value).replace(" ", "")
        best = None
        for anchor in {expected[:4], expected[-4:]}:
            start = 0
            while True:
                position = compact.find(anchor, start)
                if position < 0:
                    break
                start = position + 1
                window = compact[max(0, position - 2) : position + len(expected) + 4]
                for offset in range(len(window) - len(expected) + 1):
                    distance = edit_distance(
                        expected, window[offset : offset + len(expected)]
                    )
                    best = distance if best is None else min(best, distance)

        total_distance += len(expected) if best is None else best
        total_length += len(expected)

    assert total_length
    return total_distance / total_length


@pytest.fixture(scope="module")
def extractor():
    return DocumentExtractor()


@pytest.fixture(scope="module")
def model_service():
    return AnonymizationService(analyzer=build_analyzer())


def ocr_renders():
    return [
        (name, RENDERS / f"{name}_{suffix}")
        for name in DOCUMENTS
        for suffix in OCR_SUFFIXES
    ]


def layer_renders():
    return [(name, RENDERS / f"{name}_{LAYER_SUFFIX}") for name in DOCUMENTS]


def test_the_nine_renders_are_there():
    files = sorted(path for path in RENDERS.glob("*") if path.suffix in {".pdf", ".jpg"})

    assert len(files) == 9
    assert all(path.stat().st_size > 0 for path in files)
    assert {path.name for path in files if path.suffix == ".jpg"} == {
        f"{name}_foto.jpg" for name in DOCUMENTS
    }


@requires_ocr
@pytest.mark.parametrize(("name", "path"), layer_renders())
def test_text_layer_control_skips_ocr(extractor, name, path):
    result = extractor.extract(path.read_bytes())

    assert result.reason is None
    assert result.ocr_confidence is None
    assert cer(load_document(f"{name}.txt"), result.text) <= 0.001


@requires_ocr
@pytest.mark.parametrize(("name", "path"), ocr_renders())
def test_ocr_route_extracts_text_with_enough_confidence(extractor, name, path):
    result = extractor.extract(path.read_bytes())

    assert result.reason is None, path.name
    assert result.ocr_confidence is not None
    assert result.ocr_confidence >= 0.60
    assert cer(load_document(f"{name}.txt"), result.text) < MAX_GLOBAL_CER


@requires_ocr
def test_global_cer_meets_the_adr():
    extractor = DocumentExtractor()
    total_distance = 0
    total_length = 0
    for name, path in ocr_renders():
        reference = load_document(f"{name}.txt")
        hypothesis = extractor.extract(path.read_bytes()).text
        total_distance += edit_distance(normalise(reference), normalise(hypothesis))
        total_length += len(normalise(reference))

    measured = total_distance / total_length
    assert measured <= MAX_GLOBAL_CER, f"CER global {measured:.1%}"


@requires_ocr
def test_identifier_cer_meets_the_adr():
    extractor = DocumentExtractor()
    measured = {
        name: identifier_cer(f"{name}.txt", extractor.extract(path.read_bytes()).text)
        for name, path in ocr_renders()
    }

    for render, value in measured.items():
        assert value <= MAX_IDENTIFIER_CER, f"{render}: {value:.1%}"


@requires_ocr
def test_time_per_page_is_within_a_sane_bound(extractor):
    # El ADR mide por página (ADR-023:27-31): se divide el tiempo del documento
    # entre sus páginas. Un escaneo de dos páginas no puede contarse como una.
    for name, path in ocr_renders():
        start = time.perf_counter()
        extractor.extract(path.read_bytes())
        elapsed = time.perf_counter() - start
        pages = page_count(path)
        assert elapsed / pages < MAX_SECONDS_PER_PAGE, (
            f"{path.name}: {elapsed / pages:.1f} s por página"
        )


def page_count(path: Path) -> int:
    """Páginas del render: las del PDF, o una para un JPG."""
    if path.suffix.lower() != ".pdf":
        return 1
    document = pdfium.PdfDocument(path.read_bytes())
    try:
        return len(document)
    finally:
        document.close()


@requires_ocr
def test_no_guaranteed_entity_survives_the_pipeline(model_service):
    # Criterio medible de la validación reforzada (P1): el manifiesto de
    # ACO-051 sobre el texto que sale del OCR.
    extractor = DocumentExtractor()
    checked = 0
    for name, path in ocr_renders():
        reference = f"{name}.txt"
        extracted = extractor.extract(path.read_bytes())
        assert extracted.reason is None, path.name

        output = model_service.anonymize(extracted.text)

        if output.status == AnonymizationStatus.VALIDADO:
            assert output.anonymized_text is not None
            for entity in guaranteed_manifest_entities(reference):
                assert_manifest_entity_absent(entity, output.anonymized_text)
        else:
            assert output.anonymized_text is None
            assert output.reason is not None
            dumped = str(output.model_dump())
            for entity in guaranteed_manifest_entities(reference):
                assert entity["text"] not in dumped
        checked += 1

    assert checked == 6


@requires_ocr
def test_ocr_leaves_no_temporary_files(tmp_path, monkeypatch):
    # El EXIF no llega al OCR ni a su temporal: eso se comprueba en
    # `test_extraction.py`. Aquí, que no quede ningún fichero en el directorio
    # temporal después de extraer.
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(tmpdir))
    monkeypatch.setenv("TMPDIR", str(tmpdir))

    _, path = ocr_renders()[0]
    result = DocumentExtractor().extract(path.read_bytes())

    assert result.text
    assert {item for item in tmpdir.rglob("*") if item.is_file()} == set()
