import logging

import pytest
from fastapi.testclient import TestClient

from app.api.conversation import get_llm_gateway
from app.main import app
from app.services.llm_gateway import LLMErrorCode, LLMGateway, LLMGatewayError
from app.services.prompts import load_system_prompt

from .conftest import ANSWER, DOCUMENT_TEXT, QUESTION, FakeProvider

URL = "/api/conversation"

client = TestClient(app)


def payload(documents=None, messages=None):
    return {
        "documents": documents if documents is not None else [{"text": DOCUMENT_TEXT}],
        "messages": messages if messages is not None else [{"role": "user", "content": QUESTION}],
    }


@pytest.fixture
def use_provider(llm_env):
    """Sustituye la dependencia del gateway por uno con el proveedor simulado dado."""

    def install(provider):
        app.dependency_overrides[get_llm_gateway] = lambda: LLMGateway(provider)
        return provider

    yield install
    app.dependency_overrides.pop(get_llm_gateway, None)


def test_valid_request_returns_answer(use_provider):
    provider = use_provider(FakeProvider())

    response = client.post(URL, json=payload())

    assert response.status_code == 200
    assert response.json() == {"answer": ANSWER, "truncated": False}
    [llm_request] = provider.calls
    assert llm_request.system == load_system_prompt().text


def test_truncated_answer(use_provider):
    use_provider(FakeProvider(stop_reason="max_tokens"))

    response = client.post(URL, json=payload())

    assert response.status_code == 200
    assert response.json() == {"answer": ANSWER, "truncated": True}


def test_long_answer_is_capped_and_can_be_sent_back(use_provider):
    use_provider(FakeProvider(text="r" * 8_001))

    first = client.post(URL, json=payload())

    assert first.status_code == 200
    assert first.json() == {"answer": "r" * 8_000, "truncated": True}

    messages = [
        {"role": "user", "content": QUESTION},
        {"role": "assistant", "content": first.json()["answer"]},
        {"role": "user", "content": "Segunda pregunta inventada."},
    ]

    second = client.post(URL, json=payload(messages=messages))

    assert second.status_code == 200


def test_full_conversation_reaches_gateway(use_provider):
    provider = use_provider(FakeProvider())
    messages = [
        {"role": "user", "content": QUESTION},
        {"role": "assistant", "content": "Respuesta previa inventada."},
        {"role": "user", "content": "Segunda pregunta inventada."},
    ]

    response = client.post(URL, json=payload(messages=messages))

    assert response.status_code == 200
    [llm_request] = provider.calls
    assert [m.role for m in llm_request.messages] == ["user", "assistant", "user"]
    assert llm_request.messages[2].content == "Segunda pregunta inventada."


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(payload(documents=[]), id="no-documents"),
        pytest.param(payload(documents=[{"text": "d"}] * 4), id="too-many-documents"),
        pytest.param(payload(documents=[{"text": " "}]), id="blank-document"),
        pytest.param(payload(documents=[{"text": "d" * 30_001}]), id="long-document"),
        pytest.param(payload(messages=[]), id="no-messages"),
        pytest.param(payload(messages=[{"role": "user", "content": "p" * 2_001}]), id="long-question"),
        pytest.param(
            payload(messages=[{"role": "user", "content": "a"}, {"role": "user", "content": "b"}]),
            id="not-alternating",
        ),
        pytest.param(
            payload(messages=[{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]),
            id="ends-with-assistant",
        ),
        pytest.param({**payload(), "stream": True}, id="unknown-field"),
        pytest.param({"messages": payload()["messages"]}, id="missing-documents"),
    ],
)
def test_invalid_request_is_rejected_without_calling_gateway(use_provider, body):
    provider = use_provider(FakeProvider())

    response = client.post(URL, json=body)

    assert response.status_code == 422
    assert provider.calls == []


@pytest.mark.parametrize(
    "code, status_code, detail",
    [
        (LLMErrorCode.NOT_CONFIGURED, 503, "llm_not_configured"),
        (LLMErrorCode.RATE_LIMIT, 503, "llm_busy"),
        (LLMErrorCode.UNAVAILABLE, 503, "llm_unavailable"),
        (LLMErrorCode.AUTH, 503, "llm_unavailable"),
        (LLMErrorCode.TIMEOUT, 504, "llm_timeout"),
        (LLMErrorCode.INVALID_REQUEST, 502, "llm_error"),
        (LLMErrorCode.PROVIDER_ERROR, 502, "llm_error"),
    ],
)
def test_gateway_errors_map_to_own_codes(use_provider, code, status_code, detail):
    error = LLMGatewayError(code, status_code=418, request_id="req-test-secreto")
    use_provider(FakeProvider(error=error))

    response = client.post(URL, json=payload())

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}
    assert "req-test-secreto" not in response.text
    assert "418" not in response.text
    assert str(error) not in response.text


def test_missing_configuration_returns_503(use_provider, no_llm_env):
    no_llm_env.delenv("ANTHROPIC_API_KEY")
    provider = use_provider(FakeProvider())

    response = client.post(URL, json=payload())

    assert response.status_code == 503
    assert response.json() == {"detail": "llm_not_configured"}
    assert provider.calls == []


def test_empty_answer_returns_502(use_provider):
    use_provider(FakeProvider(text="   "))

    response = client.post(URL, json=payload())

    assert response.status_code == 502
    assert response.json() == {"detail": "llm_error"}


def all_logged_text(caplog):
    return "\n".join(record.getMessage() for record in caplog.records)


@pytest.mark.parametrize(
    "provider",
    [
        pytest.param(FakeProvider(), id="success"),
        pytest.param(FakeProvider(error=LLMGatewayError(LLMErrorCode.TIMEOUT)), id="gateway-error"),
        pytest.param(FakeProvider(text=" "), id="empty-answer"),
    ],
)
def test_logs_do_not_contain_conversation_content(use_provider, caplog, provider):
    caplog.set_level(logging.DEBUG)
    use_provider(provider)

    client.post(URL, json=payload())

    assert caplog.records, "el gateway registra al menos una línea de metadatos"
    logged = all_logged_text(caplog)
    for content in (DOCUMENT_TEXT, QUESTION, ANSWER, "[PACIENTE]", "[SANITARIO_1]"):
        assert content not in logged


def test_health_still_responds():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
