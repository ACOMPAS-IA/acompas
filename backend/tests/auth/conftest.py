"""Utilidades de los tests de autenticación (ACO-014).

Los tokens se firman con un par RSA generado en el propio test y el cliente
del JWKS se sustituye por uno con la clave pública: no se usan usuarios,
Keycloak ni red. Todos los valores son sintéticos (ADR-008).
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.api.auth import get_jwks_client
from app.api.conversation import get_llm_gateway
from app.main import app
from app.services.llm_gateway import LLMResponse

ISSUER = "http://localhost:8080/realms/acompas"
JWKS_URL = "http://keycloak:8080/realms/acompas/protocol/openid-connect/certs"
CLIENT_ID = "acompas-frontend"
KID = "clave-de-prueba"
USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
EMAIL = "paciente@example.com"

DOCUMENT_TEXT = "Informe inventado de [PACIENTE]."
QUESTION = "¿Qué significa el resultado?"
ANSWER = "Respuesta inventada del proveedor simulado."

client = TestClient(app)


@pytest.fixture(scope="session")
def signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def other_signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def make_token(
    private_key: Any,
    *,
    kid: str = KID,
    remove: tuple[str, ...] = (),
    **overrides: Any,
) -> str:
    """Token sintético con el contrato de Keycloak (ACO-013)."""
    now = datetime.now(timezone.utc)
    claims: dict[str, Any] = {
        "iss": ISSUER,
        "azp": CLIENT_ID,
        "aud": "account",
        "sub": str(USER_ID),
        "typ": "Bearer",
        "email": EMAIL,
        "realm_access": {"roles": ["paciente"]},
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    claims.update(overrides)
    for name in remove:
        claims.pop(name, None)
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": kid})


class FakeJWKSClient:
    """Cliente de claves sustituible: no usa red."""

    def __init__(self, public_key: Any, error: Exception | None = None) -> None:
        self.public_key = public_key
        self.error = error
        self.kids: list[str] = []

    def get_verification_key(self, kid: str) -> Any:
        self.kids.append(kid)
        if self.error is not None:
            raise self.error
        return self.public_key


class StubGateway:
    """Gateway de conversación simulado: registra las llamadas."""

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def complete(self, request: Any) -> LLMResponse:
        self.calls.append(request)
        return LLMResponse(
            text=ANSWER,
            model="modelo-de-prueba",
            input_tokens=1,
            output_tokens=1,
            stop_reason="end_turn",
        )


def payload() -> dict[str, Any]:
    return {
        "documents": [{"text": DOCUMENT_TEXT}],
        "messages": [{"role": "user", "content": QUESTION}],
    }


@pytest.fixture
def auth_env(monkeypatch):
    """Configuración local de la ficha (ACO-014, sección 8.1; ACO-015)."""
    monkeypatch.setenv("KEYCLOAK_ISSUER", ISSUER)
    monkeypatch.setenv("KEYCLOAK_JWKS_URL", JWKS_URL)
    monkeypatch.setenv("EMAILS_AUTORIZADOS", EMAIL)
    return monkeypatch


@pytest.fixture
def no_auth_env(monkeypatch):
    monkeypatch.delenv("KEYCLOAK_ISSUER", raising=False)
    monkeypatch.delenv("KEYCLOAK_JWKS_URL", raising=False)
    monkeypatch.delenv("EMAILS_AUTORIZADOS", raising=False)
    return monkeypatch


@pytest.fixture
def jwks(signing_key):
    provider = FakeJWKSClient(signing_key.public_key())
    app.dependency_overrides[get_jwks_client] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_jwks_client, None)


@pytest.fixture
def gateway():
    stub = StubGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: stub
    yield stub
    app.dependency_overrides.pop(get_llm_gateway, None)
