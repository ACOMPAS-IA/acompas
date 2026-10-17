import hashlib
import logging

import pytest

from app.services.llm_gateway import (
    LLMErrorCode,
    LLMGateway,
    LLMGatewayError,
    LLMMessage,
    LLMRequest,
    LLMResponse,
)
from app.services.llm_gateway.anthropic_provider import AnthropicProvider

from .conftest import FAKE_API_KEY, FAKE_MODEL

SYSTEM = "Prompt de sistema inventado para el test"
QUESTION = "Pregunta inventada sobre un texto de prueba"
ANSWER = "Respuesta inventada del proveedor simulado"


class FakeProvider:
    def __init__(self, response=None, error=None):
        self.response = response or LLMResponse(
            text=ANSWER,
            model="modelo-que-responde",
            input_tokens=11,
            output_tokens=7,
            stop_reason="end_turn",
        )
        self.error = error
        self.calls = []

    def complete(self, request, settings):
        self.calls.append((request, settings))
        if self.error is not None:
            raise self.error
        return self.response


def make_request():
    return LLMRequest(system=SYSTEM, messages=[LLMMessage(role="user", content=QUESTION)])


def gateway_log(caplog):
    return [r for r in caplog.records if r.name == "app.services.llm_gateway"]


def all_logged_text(caplog):
    return "\n".join(record.getMessage() for record in caplog.records)


def test_complete_returns_provider_response(llm_env):
    provider = FakeProvider()

    response = LLMGateway(provider).complete(make_request())

    assert response == provider.response
    assert response.text == ANSWER
    assert (response.input_tokens, response.output_tokens) == (11, 7)


def test_provider_receives_request_and_settings(llm_env):
    provider = FakeProvider()
    request = make_request()

    LLMGateway(provider).complete(request)

    [(received_request, settings)] = provider.calls
    assert received_request is request
    assert settings.model == FAKE_MODEL
    assert settings.api_key.get_secret_value() == FAKE_API_KEY


def test_settings_are_read_on_each_call(llm_env):
    provider = FakeProvider()
    gateway = LLMGateway(provider)

    gateway.complete(make_request())
    llm_env.setenv("LLM_MODEL", "otro-modelo-de-prueba")
    gateway.complete(make_request())

    assert [settings.model for _, settings in provider.calls] == [
        FAKE_MODEL,
        "otro-modelo-de-prueba",
    ]


@pytest.mark.parametrize(
    "variable, value",
    [
        ("ANTHROPIC_API_KEY", None),
        ("LLM_MODEL", None),
        ("LLM_MAX_OUTPUT_TOKENS", "no-es-un-numero"),
    ],
)
def test_not_configured_does_not_call_provider(llm_env, variable, value):
    if value is None:
        llm_env.delenv(variable)
    else:
        llm_env.setenv(variable, value)
    provider = FakeProvider()

    with pytest.raises(LLMGatewayError) as excinfo:
        LLMGateway(provider).complete(make_request())

    assert excinfo.value.code == LLMErrorCode.NOT_CONFIGURED
    assert provider.calls == []


def test_invalid_request_never_reaches_provider(llm_env):
    provider = FakeProvider()
    gateway = LLMGateway(provider)

    with pytest.raises(ValueError):
        gateway.complete(LLMRequest(system=SYSTEM, messages=[]))

    assert provider.calls == []


def test_default_provider_without_configuration(no_llm_env):
    gateway = LLMGateway()

    assert isinstance(gateway._provider, AnthropicProvider)
    with pytest.raises(LLMGatewayError) as excinfo:
        gateway.complete(make_request())
    assert excinfo.value.code == LLMErrorCode.NOT_CONFIGURED


def test_provider_error_reaches_caller_unchanged(llm_env):
    error = LLMGatewayError(LLMErrorCode.RATE_LIMIT, status_code=429, request_id="req-test-1")

    with pytest.raises(LLMGatewayError) as excinfo:
        LLMGateway(FakeProvider(error=error)).complete(make_request())

    assert excinfo.value is error


def test_successful_call_logs_only_metadata(llm_env, caplog):
    caplog.set_level(logging.INFO)

    LLMGateway(FakeProvider()).complete(make_request())

    [record] = gateway_log(caplog)
    assert record.levelno == logging.INFO
    message = record.getMessage()
    fingerprint = hashlib.sha256(SYSTEM.encode()).hexdigest()[:12]
    for expected in (
        "model=modelo-que-responde",
        "input_tokens=11",
        "output_tokens=7",
        "stop_reason=end_turn",
        "duration_ms=",
        f"system_sha256={fingerprint}",
    ):
        assert expected in message
    assert hashlib.sha256(SYSTEM.encode()).hexdigest() not in message

    logged = all_logged_text(caplog)
    for secret_or_content in (FAKE_API_KEY, SYSTEM, QUESTION, ANSWER):
        assert secret_or_content not in logged


@pytest.mark.parametrize(
    "error, expected",
    [
        (
            LLMGatewayError(LLMErrorCode.RATE_LIMIT, status_code=429, request_id="req-test-2"),
            "code=rate_limit status_code=429 request_id=req-test-2",
        ),
        (
            LLMGatewayError(LLMErrorCode.UNAVAILABLE),
            "code=unavailable status_code=None request_id=None",
        ),
    ],
)
def test_failed_call_logs_only_error_metadata(llm_env, caplog, error, expected):
    caplog.set_level(logging.INFO)

    with pytest.raises(LLMGatewayError):
        LLMGateway(FakeProvider(error=error)).complete(make_request())

    [record] = gateway_log(caplog)
    assert record.levelno == logging.INFO
    assert expected in record.getMessage()
    logged = all_logged_text(caplog)
    for secret_or_content in (FAKE_API_KEY, SYSTEM, QUESTION):
        assert secret_or_content not in logged


def test_not_configured_is_logged(no_llm_env, caplog):
    caplog.set_level(logging.INFO)

    with pytest.raises(LLMGatewayError):
        LLMGateway(FakeProvider()).complete(make_request())

    [record] = gateway_log(caplog)
    assert "code=not_configured" in record.getMessage()
