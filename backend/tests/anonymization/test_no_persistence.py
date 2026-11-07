"""Tests de no persistencia del original (ACO-025, T-03, T-04 y T-13).

Usan un analyzer falso y un servicio inyectado: no cargan el modelo ni usan
red. Los valores son sintéticos (ACO-051, ADR-008).
"""

import ast
import builtins
import io
import logging
import os
import sys
import tempfile
import traceback
import uuid
from pathlib import Path
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

URL = "/api/anonymization"
NAME = "Rosario Albendea Quintanar"
DNI = "12345678Z"
TEXT = f"Paciente: {NAME}. DNI: {DNI}."
FORBIDDEN_VALUES = (TEXT, NAME, DNI)
CONTRACT_FIELDS = {
    "status",
    "confidence",
    "anonymized_text",
    "entities_count",
    "reason",
}

# Clientes de persistencia que no deben aparecer en backend/app. La lista es
# una guarda de regresión, no una prueba de toda forma de persistencia futura.
PERSISTENCE_MODULES = {
    "alembic",
    "asyncpg",
    "boto3",
    "databases",
    "minio",
    "mongoengine",
    "motor",
    "peewee",
    "psycopg",
    "psycopg2",
    "pymongo",
    "redis",
    "sqlalchemy",
    "sqlite3",
    "tortoise",
}

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
    )


def retained_service(text):
    settings = load_settings()
    score = (settings.finding_threshold + settings.document_threshold) / 2
    return service_with(
        text,
        [("ES_DNI", text, DNI, score)],
        settings_loader=lambda: settings,
    )


def validated_service():
    return service_with(
        TEXT,
        [
            ("PERSON", TEXT, NAME),
            ("ES_DNI", TEXT, DNI),
        ],
    )


def logged_text(caplog):
    """Texto de todos los registros, incluidas sus trazas de excepción."""
    parts = []
    for record in caplog.records:
        parts.append(record.getMessage())
        if record.exc_info:
            parts.append("".join(traceback.format_exception(*record.exc_info)))
    return "\n".join(parts)


def assert_no_forbidden_values(value):
    for forbidden in FORBIDDEN_VALUES:
        assert forbidden not in value


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
def clean_environment(monkeypatch):
    monkeypatch.delenv(FINDING_THRESHOLD_ENV, raising=False)
    monkeypatch.delenv(DOCUMENT_THRESHOLD_ENV, raising=False)


@pytest.fixture
def use_service():
    def install(service):
        app.dependency_overrides[get_anonymization_service] = lambda: service

    yield install
    app.dependency_overrides.pop(get_anonymization_service, None)


def test_validated_response_has_exactly_the_contract_fields(use_service):
    use_service(validated_service())

    response = client.post(URL, json={"text": TEXT})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == CONTRACT_FIELDS
    assert body["status"] == "validado"
    assert body["anonymized_text"] == "Paciente: [PACIENTE]. DNI: [DNI]."
    assert_no_forbidden_values(response.text)


def test_retained_response_has_exactly_the_contract_fields_and_no_original(
    use_service,
):
    service = retained_service(TEXT)
    use_service(service)

    response = client.post(URL, json={"text": TEXT})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == CONTRACT_FIELDS
    assert body["status"] == "retenido"
    assert body["anonymized_text"] is None
    assert_no_forbidden_values(response.text)


@pytest.mark.parametrize("state", ["validado", "retenido", "ilegible"])
def test_logs_do_not_contain_the_original_in_the_three_states(
    use_service, caplog, state
):
    if state == "validado":
        use_service(validated_service())
        text = TEXT
    elif state == "retenido":
        use_service(retained_service(TEXT))
        text = TEXT
    else:
        use_service(service_with("", []))
        text = ""

    caplog.set_level(logging.INFO)

    response = client.post(URL, json={"text": text})

    assert response.status_code == 200
    assert_no_forbidden_values(logged_text(caplog))


@pytest.mark.parametrize(
    ("payload", "expected_detail"),
    [
        ({"texto": TEXT}, "invalid_request"),
        ({"text": "MARCADOR_SECRETO " + TEXT + "a" * 30_000}, "text_too_long"),
    ],
)
def test_validation_errors_do_not_log_or_echo_the_text(
    caplog, payload, expected_detail
):
    caplog.set_level(logging.INFO)

    response = client.post(URL, json=payload)

    assert response.status_code == 422
    assert response.json() == {"detail": expected_detail}
    assert_no_forbidden_values(response.text)
    assert_no_forbidden_values(logged_text(caplog))
    assert "MARCADOR_SECRETO" not in logged_text(caplog)


def test_unexpected_error_does_not_echo_or_log_the_text(use_service, caplog):
    use_service(ExplodingService())
    failing_client = TestClient(app, raise_server_exceptions=False)
    caplog.set_level(logging.INFO)

    response = failing_client.post(URL, json={"text": TEXT})

    assert response.status_code == 500
    assert_no_forbidden_values(response.text)
    assert_no_forbidden_values(logged_text(caplog))


def test_unexpected_error_is_sanitized_before_uvicorn_logs_it(use_service, caplog):
    use_service(ExplodingService())
    caplog.set_level(logging.INFO)

    with pytest.raises(RuntimeError) as excinfo:
        client.post(URL, json={"text": TEXT})

    error = excinfo.value
    rendered = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    assert str(error) == "anonymization_failed"
    assert error.__cause__ is None
    assert error.__suppress_context__ is True
    assert_no_forbidden_values(rendered)
    assert_no_forbidden_values(logged_text(caplog))


def snapshot(root):
    return {str(path) for path in Path(root).rglob("*") if path.is_file()}


def test_request_creates_no_files(use_service, tmp_path, monkeypatch):
    workdir = tmp_path / "work"
    tmpdir = tmp_path / "tmp"
    workdir.mkdir()
    tmpdir.mkdir()

    monkeypatch.chdir(workdir)
    monkeypatch.setattr(tempfile, "tempdir", str(tmpdir))
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    # Evita que la importación perezosa de un módulo escriba un .pyc y se
    # confunda con una persistencia del documento.
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    use_service(validated_service())

    writes = []
    real_io_open = io.open
    real_builtins_open = builtins.open
    real_os_open = os.open
    write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC

    def guard_io_open(file, mode="r", *args, **kwargs):
        if any(flag in mode for flag in "wax+"):
            writes.append(str(file))
            raise AssertionError(f"escritura de fichero: {file}")
        return real_io_open(file, mode, *args, **kwargs)

    def guard_builtins_open(file, mode="r", *args, **kwargs):
        if any(flag in mode for flag in "wax+"):
            writes.append(str(file))
            raise AssertionError(f"escritura de fichero: {file}")
        return real_builtins_open(file, mode, *args, **kwargs)

    def guard_os_open(path, flags, *args, **kwargs):
        if flags & write_flags:
            writes.append(str(path))
            raise AssertionError(f"escritura de fichero: {path}")
        return real_os_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(io, "open", guard_io_open)
    monkeypatch.setattr(builtins, "open", guard_builtins_open)
    monkeypatch.setattr(os, "open", guard_os_open)

    with TestClient(app) as test_client:
        before = snapshot(workdir) | snapshot(tmpdir)
        response = test_client.post(URL, json={"text": TEXT})
        after = snapshot(workdir) | snapshot(tmpdir)

    assert response.status_code == 200
    assert writes == []
    assert after == before


def imported_roots(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.split(".")[0]


def test_app_does_not_import_persistence_clients():
    app_dir = Path(__file__).resolve().parents[2] / "app"
    offenders = [
        f"{path.relative_to(app_dir)}: {module}"
        for path in app_dir.rglob("*.py")
        for module in imported_roots(path)
        if module in PERSISTENCE_MODULES
    ]

    assert offenders == []
