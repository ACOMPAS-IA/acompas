"""Exposición de la API key en respuestas HTTP (ACO-028, T-39)."""

import uuid

import anthropic
import httpx2
import pytest
from fastapi.testclient import TestClient

from app.api.auth import get_current_user
from app.api.conversation import get_llm_gateway
from app.main import app
from app.services.auth import Principal
from app.services.llm_gateway import LLMGateway
from app.services.llm_gateway.anthropic_provider import AnthropicProvider

from .conftest import FAKE_MODEL

# Se construye por partes para no dejar un literal con forma de clave en el
# repositorio. En tiempo de ejecución tiene el prefijo de las claves de Anthropic.
SENTINEL_API_KEY = "sk-" + "ant-" + "centinela-de-pruebas-0123456789abcdef"

DOCUMENT = "Informe inventado de [PACIENTE]. Marcador tumoral en rango."
QUESTION = "¿Qué significa que el marcador esté en rango?"
ANSWER = "Respuesta inventada del proveedor."
URL = "/api/conversation"


def payload():
    return {
        "documents": [{"text": DOCUMENT}],
        "messages": [{"role": "user", "content": QUESTION}],
    }


def sdk_response(text=ANSWER):
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": "modelo-que-responde",
        "content": [{"type": "text", "text": text}],
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 13, "output_tokens": 8},
    }


def mock_factory(handler):
    def factory(**kwargs):
        kwargs["http_client"] = anthropic.DefaultHttpxClient(
            trust_env=False, transport=httpx2.MockTransport(handler)
        )
        return anthropic.Anthropic(**kwargs)

    return factory


@pytest.fixture(autouse=True)
def authenticated_user():
    """El endpoint está protegido (ACO-014); estas pruebas cubren la clave (ACO-028)."""
    app.dependency_overrides[get_current_user] = lambda: Principal(
        user_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        email="paciente@example.com",
        roles=frozenset({"paciente"}),
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def sentinel_env(no_llm_env):
    no_llm_env.setenv("ANTHROPIC_API_KEY", SENTINEL_API_KEY)
    no_llm_env.setenv("LLM_MODEL", FAKE_MODEL)
    return no_llm_env


@pytest.fixture
def install_gateway():
    def install(handler):
        app.dependency_overrides[get_llm_gateway] = lambda: LLMGateway(
            AnthropicProvider(mock_factory(handler))
        )

    yield install
    app.dependency_overrides.pop(get_llm_gateway, None)


def test_sentinel_key_not_in_success_response(sentinel_env, install_gateway):
    def handler(request):
        return httpx2.Response(200, json=sdk_response())

    install_gateway(handler)

    response = TestClient(app).post(URL, json=payload())

    assert response.status_code == 200
    assert response.json()["answer"] == ANSWER
    assert SENTINEL_API_KEY not in response.text


def test_sentinel_key_not_in_error_response(sentinel_env, install_gateway):
    def handler(request):
        return httpx2.Response(
            401,
            json={
                "type": "error",
                "error": {"type": "authentication_error", "message": "clave rechazada"},
            },
        )

    install_gateway(handler)

    response = TestClient(app).post(URL, json=payload())

    assert response.status_code == 503
    assert response.json() == {"detail": "llm_unavailable"}
    assert SENTINEL_API_KEY not in response.text


def test_unsupported_variable_returns_llm_not_configured(sentinel_env):
    sentinel_env.setenv("ANTHROPIC_BASE_URL", "https://proxy-inventado.example")

    response = TestClient(app).post(URL, json=payload())

    assert response.status_code == 503
    assert response.json() == {"detail": "llm_not_configured"}
    assert "proxy-inventado.example" not in response.text
