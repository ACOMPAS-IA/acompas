"""Tests del contrato HTTP de la anonimización (ACO-024, AC-01 a AC-10).

Usan un analyzer falso y un servicio inyectado: no cargan el modelo ni usan
red. Los valores son sintéticos (ACO-051, ADR-008).
"""

import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.anonymization import get_anonymization_service
from app.api.auth import get_current_user, get_jwks_client
from app.main import app
from app.services.anonymization import AnonymizationService
from app.services.anonymization.config import (
    DOCUMENT_THRESHOLD_ENV,
    FINDING_THRESHOLD_ENV,
    load_settings,
)
from app.services.auth import Principal
from app.services.auth.config import ISSUER_ENV, JWKS_URL_ENV

URL = "/api/anonymization"
TEXT = "Paciente: Rosario Albendea Quintanar. DNI: 12345678Z."
DNI_TEXT = "DNI: 12345678Z."

client = TestClient(app)


class FakeAnalyzer:
    def __init__(self, results=()):
        self.results = list(results)
        self.calls = 0

    def analyze(self, text, language, entities):
        self.calls += 1
        return self.results


class ExplodingService:
    def anonymize(self, text):
        raise RuntimeError(text)


def detection(entity_type, text, fragment, score=1.0):
    start = text.index(fragment)
    return SimpleNamespace(
        entity_type=entity_type,
        start=start,
        end=start + len(fragment),
        score=score,
    )


def service_with(text, results, settings_loader=load_settings):
    analyzer = FakeAnalyzer([detection(*item) for item in results])
    return AnonymizationService(
        analyzer=analyzer, settings_loader=settings_loader
    ), analyzer


@pytest.fixture(autouse=True)
def authenticated_user():
    """El endpoint está protegido; el contrato se prueba ya autenticado."""
    app.dependency_overrides[get_current_user] = lambda: Principal(
        user_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        email="paciente@example.com",
        roles=frozenset({"paciente"}),
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(autouse=True)
def fake_jwks():
    """Evita construir el cliente JWKS cuando se prueba el 401 sin token."""
    app.dependency_overrides[get_jwks_client] = lambda: None
    yield
    app.dependency_overrides.pop(get_jwks_client, None)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.delenv(FINDING_THRESHOLD_ENV, raising=False)
    monkeypatch.delenv(DOCUMENT_THRESHOLD_ENV, raising=False)


@pytest.fixture
def use_service():
    """Sustituye la dependencia del servicio por uno sin modelo."""

    def install(service):
        app.dependency_overrides[get_anonymization_service] = lambda: service

    yield install
    app.dependency_overrides.pop(get_anonymization_service, None)


def test_validated_request_returns_anonymized_text(use_service):
    service, analyzer = service_with(
        TEXT,
        [
            ("PERSON", TEXT, "Rosario Albendea Quintanar"),
            ("ES_DNI", TEXT, "12345678Z"),
        ],
    )
    use_service(service)

    response = client.post(URL, json={"text": TEXT})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "validado"
    assert body["anonymized_text"] == "Paciente: [PACIENTE]. DNI: [DNI]."
    assert body["entities_count"] == {"PACIENTE": 1, "ES_DNI": 1}
    assert body["confidence"] == pytest.approx(1.0)
    assert body["reason"] is None
    assert analyzer.calls == 1


def test_retained_document_has_no_text(use_service):
    service, _ = service_with(
        DNI_TEXT, [("ES_DNI", DNI_TEXT, "12345678Z", 0.5)]
    )
    use_service(service)

    response = client.post(URL, json={"text": DNI_TEXT})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "retenido"
    assert body["confidence"] == pytest.approx(0.5)
    assert body["anonymized_text"] is None
    assert body["entities_count"] == {}
    assert body["reason"] == "baja_confianza"
    assert "12345678Z" not in response.text


@pytest.mark.parametrize("text", ["", "   ", "\n\t "])
def test_empty_text_is_illegible_without_calling_the_model(use_service, text):
    service, analyzer = service_with(text, [])
    use_service(service)

    response = client.post(URL, json={"text": text})

    assert response.status_code == 200
    assert response.json() == {
        "status": "ilegible",
        "confidence": None,
        "anonymized_text": None,
        "entities_count": {},
        "reason": "texto_vacio",
    }
    assert analyzer.calls == 0


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"text": 12345},
        {"texto": "SECRETO"},
    ],
)
def test_invalid_body_returns_invalid_request_without_echo(payload):
    response = client.post(URL, json=payload)

    assert response.status_code == 422
    assert response.json() == {"detail": "invalid_request"}
    assert "SECRETO" not in response.text
    assert "12345" not in response.text


def test_malformed_json_returns_invalid_request_without_echo():
    response = client.post(
        URL, content="{", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "invalid_request"}


def test_too_long_text_is_rejected_without_echo():
    text = "SECRETO" + "a" * 30_000

    response = client.post(URL, json={"text": text})

    assert response.status_code == 422
    assert response.json() == {"detail": "text_too_long"}
    assert "SECRETO" not in response.text


def test_maximum_length_is_accepted(use_service):
    text = "a" * 30_000
    service, _ = service_with(text, [])
    use_service(service)

    response = client.post(URL, json={"text": text})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "validado"
    assert body["confidence"] == 1.0
    assert body["anonymized_text"] == text
    assert body["entities_count"] == {}


def test_invalid_thresholds_return_503(use_service, monkeypatch):
    monkeypatch.setenv(FINDING_THRESHOLD_ENV, "0.9")
    monkeypatch.setenv(DOCUMENT_THRESHOLD_ENV, "0.5")
    service, analyzer = service_with(TEXT, [])
    use_service(service)

    response = client.post(URL, json={"text": TEXT})

    assert response.status_code == 503
    assert response.json() == {"detail": "anonymization_not_configured"}
    assert analyzer.calls == 0


def test_missing_token_is_rejected(monkeypatch):
    monkeypatch.setenv(ISSUER_ENV, "http://localhost:8080/realms/acompas")
    monkeypatch.setenv(
        JWKS_URL_ENV,
        "http://keycloak:8080/realms/acompas/protocol/openid-connect/certs",
    )
    app.dependency_overrides.pop(get_current_user, None)

    response = client.post(URL, json={"text": TEXT})

    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}


def test_route_is_documented():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert URL in response.json()["paths"]


def test_internal_error_does_not_echo_the_text(use_service):
    use_service(ExplodingService())
    failing_client = TestClient(app, raise_server_exceptions=False)

    response = failing_client.post(URL, json={"text": TEXT})

    assert response.status_code == 500
    assert TEXT not in response.text


def test_response_does_not_contain_synthetic_values(use_service):
    service, _ = service_with(
        TEXT,
        [
            ("PERSON", TEXT, "Rosario Albendea Quintanar"),
            ("ES_DNI", TEXT, "12345678Z"),
        ],
    )
    use_service(service)

    response = client.post(URL, json={"text": TEXT})

    assert response.status_code == 200
    assert "Rosario Albendea Quintanar" not in response.text
    assert "12345678Z" not in response.text
