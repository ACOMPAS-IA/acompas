"""Contrato HTTP de la autenticación (ACO-014, AC-01 a AC-08)."""

import logging
from datetime import datetime, timedelta, timezone

import pytest

from app.api.auth import get_jwks_client
from app.main import app
from app.services.auth import AuthError, AuthErrorCode

from .conftest import (
    ANSWER,
    USER_ID,
    FakeJWKSClient,
    client,
    make_token,
    payload,
)

URL = "/api/conversation"


@pytest.fixture(autouse=True)
def auth(auth_env, jwks, gateway):
    """Configuración, clave fija y gateway simulado en las pruebas de API."""
    return jwks


def post(token: str | None = None, headers: dict[str, str] | None = None):
    if headers is None:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post(URL, json=payload(), headers=headers)


def test_valid_patient_token_reaches_endpoint(signing_key, gateway):
    response = post(make_token(signing_key))

    assert response.status_code == 200
    assert response.json() == {"answer": ANSWER, "truncated": False}
    assert len(gateway.calls) == 1


def test_valid_admin_token_reaches_endpoint(signing_key, gateway):
    token = make_token(signing_key, realm_access={"roles": ["administrador"]})

    assert post(token).status_code == 200


@pytest.mark.parametrize(
    "headers",
    [
        pytest.param({}, id="no-header"),
        pytest.param(
            {"Authorization": "Basic dXN1YXJpbzpjbGF2ZQ=="}, id="basic-scheme"
        ),
        pytest.param({"Authorization": "Bearer no-es-un-jwt"}, id="malformed"),
    ],
)
def test_absent_or_malformed_token_is_401(gateway, headers):
    response = post(headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert gateway.calls == []


def test_unauthenticated_invalid_body_is_401(gateway):
    # La autenticación se resuelve antes que el cuerpo: no se filtra el detalle
    # de validación a una petición sin token.
    response = client.post(URL, json={})

    assert response.status_code == 401
    assert gateway.calls == []


@pytest.mark.parametrize(
    "overrides, remove",
    [
        pytest.param(
            {"exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
            (),
            id="expired",
        ),
        pytest.param({"iss": "http://otro:8080/realms/acompas"}, (), id="wrong-issuer"),
        pytest.param({"azp": "otro-cliente"}, (), id="wrong-azp"),
        pytest.param({"typ": "ID"}, (), id="id-token"),
        pytest.param({"sub": "no-es-un-uuid"}, (), id="subject-not-uuid"),
        pytest.param({}, ("exp",), id="missing-exp"),
    ],
)
def test_invalid_token_is_401(signing_key, gateway, overrides, remove):
    response = post(make_token(signing_key, remove=remove, **overrides))

    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert gateway.calls == []


def test_signature_from_another_key_is_401(signing_key, other_signing_key, gateway):
    response = post(make_token(other_signing_key))

    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}
    assert gateway.calls == []


def test_unknown_kid_is_401_not_503(signing_key, gateway):
    app.dependency_overrides[get_jwks_client] = lambda: FakeJWKSClient(
        signing_key.public_key(), error=AuthError(AuthErrorCode.INVALID_TOKEN)
    )

    response = post(make_token(signing_key, kid="kid-desconocido"))

    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}
    assert gateway.calls == []


def test_token_without_app_role_is_403(signing_key, gateway):
    token = make_token(signing_key, realm_access={"roles": ["otro"]})

    response = post(token)

    assert response.status_code == 403
    assert response.json() == {"detail": "forbidden"}
    assert "WWW-Authenticate" not in response.headers
    assert gateway.calls == []


def test_unavailable_jwks_is_503(signing_key, gateway):
    app.dependency_overrides[get_jwks_client] = lambda: FakeJWKSClient(
        signing_key.public_key(), error=AuthError(AuthErrorCode.UNAVAILABLE)
    )

    response = post(make_token(signing_key))

    assert response.status_code == 503
    assert response.json() == {"detail": "auth_unavailable"}
    assert gateway.calls == []


def test_missing_configuration_is_503(monkeypatch, gateway):
    monkeypatch.delenv("KEYCLOAK_ISSUER", raising=False)
    monkeypatch.delenv("KEYCLOAK_JWKS_URL", raising=False)

    response = post()

    assert response.status_code == 503
    assert response.json() == {"detail": "auth_unavailable"}
    assert gateway.calls == []


def test_token_is_not_exposed(signing_key, caplog, gateway):
    caplog.set_level(logging.DEBUG)
    token = make_token(
        signing_key, exp=datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    response = post(token)

    assert response.status_code == 401
    assert token not in response.text
    assert str(USER_ID) not in response.text
    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert token not in logged
    assert str(USER_ID) not in logged


def test_health_is_public_without_token(monkeypatch):
    monkeypatch.delenv("KEYCLOAK_ISSUER", raising=False)
    monkeypatch.delenv("KEYCLOAK_JWKS_URL", raising=False)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
