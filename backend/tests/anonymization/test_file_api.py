"""Tests del contrato del endpoint de ficheros (ACO-035, secciones 8 y 10).

No cargan Tesseract ni el modelo: el extractor y el servicio se sustituyen por
dobles. Los valores son sintéticos (ACO-051, ADR-008).
"""

import logging
import tempfile
import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.anonymization import get_anonymization_service, get_document_extractor
from app.api.auth import get_current_user, get_jwks_client
from app.main import app
from app.services.anonymization import AnonymizationService
from app.services.anonymization.models import (
    REASON_EMPTY_TEXT,
    REASON_LOW_OCR_CONFIDENCE,
)
from app.services.auth import Principal
from app.services.auth.config import ISSUER_ENV, JWKS_URL_ENV
from app.services.extraction import (
    ExtractionConfigurationError,
    ExtractionResult,
    FileTooLargeError,
    TextTooLongError,
    UnsupportedFormatError,
)

URL = "/api/anonymization/file"
TEXT = "Paciente: Rosario Albendea Quintanar. DNI: 12345678Z."
PDF_BYTES = b"%PDF-1.7\n" + b"0" * 512

client = TestClient(app)


class FakeAnalyzer:
    def __init__(self, results=()):
        self.results = list(results)
        self.calls = 0

    def analyze(self, text, language, entities):
        self.calls += 1
        return self.results


class FakeExtractor:
    """Extractor doble: devuelve un resultado fijo o lanza lo que se le pida."""

    def __init__(self, result=None, error=None):
        self.result = result or ExtractionResult(text=TEXT)
        self.error = error
        self.calls = 0

    def extract(self, data):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.result


def detection(entity_type, text, value, score=1.0):
    start = text.index(value)
    return SimpleNamespace(
        entity_type=entity_type,
        start=start,
        end=start + len(value),
        score=score,
    )


def service_with(text, results):
    analyzer = FakeAnalyzer([detection(*item) for item in results])
    return AnonymizationService(analyzer=analyzer), analyzer


def install(extractor, service=None):
    app.dependency_overrides[get_document_extractor] = lambda: extractor
    if service is not None:
        app.dependency_overrides[get_anonymization_service] = lambda: service
    return extractor


@pytest.fixture(autouse=True)
def authenticated_user():
    app.dependency_overrides[get_current_user] = lambda: Principal(
        user_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        email="paciente@example.com",
        roles=frozenset({"paciente"}),
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(autouse=True)
def fake_jwks():
    app.dependency_overrides[get_jwks_client] = lambda: None
    yield
    app.dependency_overrides.pop(get_jwks_client, None)


@pytest.fixture(autouse=True)
def clean_overrides():
    yield
    app.dependency_overrides.pop(get_document_extractor, None)
    app.dependency_overrides.pop(get_anonymization_service, None)


def post(data=PDF_BYTES, filename="informe.pdf", content_type="application/pdf"):
    return client.post(URL, files={"file": (filename, data, content_type)})


def test_file_is_anonymised_with_the_same_contract(clean_overrides):
    service, analyzer = service_with(
        TEXT,
        [
            ("PERSON", TEXT, "Rosario Albendea Quintanar"),
            ("ES_DNI", TEXT, "12345678Z"),
        ],
    )
    install(FakeExtractor(), service)

    response = post()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "validado"
    assert body["anonymized_text"] == "Paciente: [PACIENTE]. DNI: [DNI]."
    assert body["entities_count"] == {"PACIENTE": 1, "ES_DNI": 1}
    assert body["reason"] is None
    assert body["confidence"] == pytest.approx(1.0)
    assert analyzer.calls == 1
    assert "Rosario Albendea Quintanar" not in response.text
    assert "12345678Z" not in response.text


@pytest.mark.parametrize(
    ("reason", "expected"),
    [
        (REASON_EMPTY_TEXT, "texto_vacio"),
        (REASON_LOW_OCR_CONFIDENCE, "baja_confianza_ocr"),
    ],
)
def test_illegible_document_does_not_reach_the_anonymiser(reason, expected):
    service, analyzer = service_with(TEXT, [])
    install(FakeExtractor(ExtractionResult(text="", reason=reason)), service)

    response = post()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ilegible"
    assert body["reason"] == expected
    assert body["anonymized_text"] is None
    assert body["entities_count"] == {}
    assert analyzer.calls == 0


def test_file_too_large_returns_413():
    install(FakeExtractor(error=FileTooLargeError("grande")))

    response = post()

    assert response.status_code == 413
    assert response.json() == {"detail": "file_too_large"}


def test_twenty_megabytes_and_one_byte_returns_413(clean_overrides):
    # Con el extractor real: el corte lo hace el tamaño, antes de leer nada.
    from app.services.extraction import DocumentExtractor
    from app.services.extraction.service import MAX_UPLOAD_BYTES

    app.dependency_overrides[get_document_extractor] = DocumentExtractor
    payload = b"%PDF-1.7\n" + b"0" * (MAX_UPLOAD_BYTES + 1 - len(b"%PDF-1.7\n"))

    response = post(payload)

    assert response.status_code == 413
    assert response.json() == {"detail": "file_too_large"}
    assert b"0" * 100 not in response.content


def test_unsupported_format_returns_415():
    install(FakeExtractor(error=UnsupportedFormatError("firma")))

    response = post()

    assert response.status_code == 415
    assert response.json() == {"detail": "unsupported_format"}


def test_text_too_long_returns_422():
    install(FakeExtractor(error=TextTooLongError("tope")))

    response = post()

    assert response.status_code == 422
    assert response.json() == {"detail": "text_too_long"}


def test_invalid_extraction_configuration_returns_503():
    install(FakeExtractor(error=ExtractionConfigurationError("umbral")))

    response = post()

    assert response.status_code == 503
    assert response.json() == {"detail": "extraction_not_configured"}


def test_missing_file_field_returns_invalid_request_without_echo():
    response = client.post(URL, files={"otro": ("x.pdf", b"%PDF-", "application/pdf")})

    assert response.status_code == 422
    assert response.json() == {"detail": "invalid_request"}
    assert "x.pdf" not in response.text


def test_json_body_is_rejected_without_echo():
    response = client.post(URL, json={"text": TEXT})

    assert response.status_code == 422
    assert response.json() == {"detail": "invalid_request"}
    assert "Rosario" not in response.text


def test_filename_is_not_echoed_nor_logged(clean_overrides, caplog):
    filename = "informe_sintetico_rosario.pdf"
    service, _ = service_with(TEXT, [])
    install(FakeExtractor(), service)
    caplog.set_level(logging.INFO)

    response = post(filename=filename)

    assert response.status_code == 200
    assert filename not in response.text
    assert filename not in caplog.text


def test_unexpected_extractor_error_is_sanitised(caplog):
    install(FakeExtractor(error=RuntimeError(TEXT)))
    failing_client = TestClient(app, raise_server_exceptions=False)
    caplog.set_level(logging.INFO)

    response = failing_client.post(
        URL, files={"file": ("informe.pdf", PDF_BYTES, "application/pdf")}
    )

    assert response.status_code == 500
    assert TEXT not in response.text
    assert TEXT not in caplog.text


def test_missing_token_is_rejected(monkeypatch):
    monkeypatch.setenv(ISSUER_ENV, "http://localhost:8080/realms/acompas")
    monkeypatch.setenv(
        JWKS_URL_ENV,
        "http://keycloak:8080/realms/acompas/protocol/openid-connect/certs",
    )
    app.dependency_overrides.pop(get_current_user, None)

    response = post()

    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}


def test_route_is_documented():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert URL in response.json()["paths"]


def test_upload_over_one_megabyte_leaves_no_residue(tmp_path, monkeypatch):
    workdir = tmp_path / "work"
    tmpdir = tmp_path / "tmp"
    workdir.mkdir()
    tmpdir.mkdir()

    monkeypatch.chdir(workdir)
    monkeypatch.setattr(tempfile, "tempdir", str(tmpdir))
    monkeypatch.setenv("TMPDIR", str(tmpdir))

    install(FakeExtractor())
    payload = b"%PDF-1.7\n" + b"0" * 1_100_000
    assert len(payload) > 1024 * 1024  # supera el límite del fichero en memoria

    with TestClient(app) as test_client:
        response = test_client.post(
            URL, files={"file": ("informe.pdf", payload, "application/pdf")}
        )
        after = {path for path in tmpdir.rglob("*") if path.is_file()}

    assert response.status_code == 200
    assert after == set()
    assert list(workdir.rglob("*")) == []
