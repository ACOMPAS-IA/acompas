import logging
from types import SimpleNamespace

import anthropic
import httpx
import httpx2
import pytest

from app.services.llm_gateway import (
    LLMErrorCode,
    LLMGateway,
    LLMGatewayError,
    LLMMessage,
    LLMRequest,
)
from app.services.llm_gateway.anthropic_provider import AnthropicProvider
from app.services.llm_gateway.config import load_settings

from .conftest import FAKE_API_KEY, FAKE_MODEL

SYSTEM = "Prompt de sistema inventado para el test"
QUESTION = "Pregunta inventada sobre un texto de prueba"
# Marcador del mensaje del proveedor: no debe llegar a quien llama ni a los registros.
PROVIDER_MESSAGE = f"MENSAJE-DEL-PROVEEDOR que repite: {QUESTION}"


def sdk_message(*blocks, model="modelo-que-responde", stop_reason="end_turn"):
    return SimpleNamespace(
        content=list(blocks),
        model=model,
        usage=SimpleNamespace(input_tokens=13, output_tokens=8),
        stop_reason=stop_reason,
    )


def text_block(text):
    return SimpleNamespace(type="text", text=text)


class FakeClientFactory:
    """Sustituye a anthropic.Anthropic: registra la construcción y la llamada."""

    def __init__(self, message=None, error=None):
        self.message = message or sdk_message(text_block("Respuesta inventada"))
        self.error = error
        self.client_kwargs = None
        self.create_kwargs = None

    def __call__(self, **kwargs):
        self.client_kwargs = kwargs
        return SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.create_kwargs = kwargs
        if self.error is not None:
            raise self.error
        return self.message


def make_request(**kwargs):
    return LLMRequest(
        system=SYSTEM,
        messages=[
            LLMMessage(role="user", content=QUESTION),
            LLMMessage(role="assistant", content="Respuesta anterior inventada"),
            LLMMessage(role="user", content="Segunda pregunta inventada"),
        ],
        **kwargs,
    )


def mock_response(text="Respuesta inventada"):
    return httpx2.Response(
        200,
        json={
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "model": "modelo-que-responde",
            "content": [{"type": "text", "text": text}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 13, "output_tokens": 8},
        },
    )


def mock_client_factory(handler, captured):
    """Construye el cliente real con MockTransport, conservando los kwargs del proveedor."""

    def factory(**kwargs):
        captured.update(kwargs)
        kwargs["http_client"] = anthropic.DefaultHttpxClient(
            trust_env=False, transport=httpx2.MockTransport(handler)
        )
        return anthropic.Anthropic(**kwargs)

    return factory


def test_sends_configuration_and_request_to_sdk(llm_env):
    llm_env.setenv("LLM_MAX_OUTPUT_TOKENS", "300")
    llm_env.setenv("LLM_TIMEOUT_SECONDS", "15")
    llm_env.setenv("LLM_MAX_RETRIES", "1")
    factory = FakeClientFactory()

    AnthropicProvider(factory).complete(make_request(), load_settings())

    client_kwargs = factory.client_kwargs
    assert set(client_kwargs) == {
        "api_key",
        "base_url",
        "open_telemetry",
        "http_client",
        "timeout",
        "max_retries",
    }
    assert client_kwargs["api_key"] == FAKE_API_KEY
    assert client_kwargs["base_url"] == "https://api.anthropic.com"
    assert client_kwargs["open_telemetry"] is False
    assert client_kwargs["timeout"] == 15.0
    assert client_kwargs["max_retries"] == 1
    assert isinstance(client_kwargs["http_client"], anthropic.DefaultHttpxClient)
    assert client_kwargs["http_client"].trust_env is False
    assert factory.create_kwargs == {
        "model": FAKE_MODEL,
        "system": SYSTEM,
        "messages": [
            {"role": "user", "content": QUESTION},
            {"role": "assistant", "content": "Respuesta anterior inventada"},
            {"role": "user", "content": "Segunda pregunta inventada"},
        ],
        "max_tokens": 300,
    }


def test_uses_official_endpoint_and_api_key_header(llm_env):
    captured = {}
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["headers"] = dict(request.headers)
        return mock_response()

    response = AnthropicProvider(mock_client_factory(handler, captured)).complete(
        make_request(), load_settings()
    )

    assert seen["url"] == "https://api.anthropic.com/v1/messages"
    assert seen["headers"]["x-api-key"] == FAKE_API_KEY
    assert "authorization" not in seen["headers"]
    assert response.text == "Respuesta inventada"
    assert captured["base_url"] == "https://api.anthropic.com"
    assert captured["open_telemetry"] is False
    assert isinstance(captured["http_client"], anthropic.DefaultHttpxClient)
    assert captured["http_client"].trust_env is False


# Señuelos inventados: no apuntan a ningún proxy ni certificado real.
PROXY_DECOYS = {
    "HTTP_PROXY": "http://proxy-inventado.example:3128",
    "HTTPS_PROXY": "http://proxy-inventado.example:3128",
    "ALL_PROXY": "socks5://proxy-inventado.example:1080",
    "NO_PROXY": "api.anthropic.com",
    "SSL_CERT_FILE": "/tmp/certificado-inventado.pem",
    "SSL_CERT_DIR": "/tmp/certificados-inventados",
}


@pytest.mark.parametrize("variable, value", list(PROXY_DECOYS.items()))
def test_environment_network_decoys_do_not_alter_request(llm_env, variable, value):
    llm_env.setenv(variable, value)
    captured = {}
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["headers"] = dict(request.headers)
        return mock_response()

    AnthropicProvider(mock_client_factory(handler, captured)).complete(
        make_request(), load_settings()
    )

    assert seen["url"] == "https://api.anthropic.com/v1/messages"
    assert seen["headers"]["x-api-key"] == FAKE_API_KEY
    assert captured["http_client"].trust_env is False
    # El SDK 1.17.0 crea mounts de proxy desde el entorno aunque trust_env=False;
    # el transporte explícito debe dejar el cliente sin mounts.
    assert captured["http_client"]._mounts == {}


def test_request_max_output_tokens_overrides_configuration(llm_env):
    factory = FakeClientFactory()

    AnthropicProvider(factory).complete(make_request(max_output_tokens=50), load_settings())

    assert factory.create_kwargs["max_tokens"] == 50


def test_builds_response_from_text_blocks(llm_env):
    factory = FakeClientFactory(
        sdk_message(
            SimpleNamespace(type="thinking", thinking=""),
            text_block("Primera parte. "),
            text_block("Segunda parte."),
            stop_reason="max_tokens",
        )
    )

    response = AnthropicProvider(factory).complete(make_request(), load_settings())

    assert response.text == "Primera parte. Segunda parte."
    assert response.model == "modelo-que-responde"
    assert (response.input_tokens, response.output_tokens) == (13, 8)
    assert response.stop_reason == "max_tokens"


REQUEST = httpx.Request("POST", "https://api.anthropic.com/v1/messages")


def status_error(error_class, status_code):
    response = httpx.Response(
        status_code, request=REQUEST, headers={"request-id": f"req-test-{status_code}"}
    )
    return error_class(PROVIDER_MESSAGE, response=response, body=None)


STATUS_CASES = [
    (anthropic.BadRequestError, 400, LLMErrorCode.INVALID_REQUEST),
    (anthropic.AuthenticationError, 401, LLMErrorCode.AUTH),
    (anthropic.APIStatusError, 402, LLMErrorCode.PROVIDER_ERROR),
    (anthropic.PermissionDeniedError, 403, LLMErrorCode.AUTH),
    (anthropic.NotFoundError, 404, LLMErrorCode.INVALID_REQUEST),
    (anthropic.APIStatusError, 408, LLMErrorCode.TIMEOUT),
    (anthropic.ConflictError, 409, LLMErrorCode.PROVIDER_ERROR),
    (anthropic.APIStatusError, 413, LLMErrorCode.INVALID_REQUEST),
    (anthropic.UnprocessableEntityError, 422, LLMErrorCode.INVALID_REQUEST),
    (anthropic.RateLimitError, 429, LLMErrorCode.RATE_LIMIT),
    (anthropic.InternalServerError, 500, LLMErrorCode.UNAVAILABLE),
    (anthropic.InternalServerError, 503, LLMErrorCode.UNAVAILABLE),
    (anthropic.InternalServerError, 529, LLMErrorCode.UNAVAILABLE),
]


def assert_clean_error(error, code):
    assert isinstance(error, LLMGatewayError)
    assert error.code == code
    assert error.__cause__ is None
    assert error.__context__ is None
    assert "MENSAJE-DEL-PROVEEDOR" not in str(error)
    assert QUESTION not in str(error)
    assert FAKE_API_KEY not in str(error)


@pytest.mark.parametrize(
    "error_class, status_code, code",
    STATUS_CASES,
    ids=[f"{status}-{code}" for _, status, code in STATUS_CASES],
)
def test_status_errors_are_converted(llm_env, error_class, status_code, code):
    factory = FakeClientFactory(error=status_error(error_class, status_code))

    with pytest.raises(LLMGatewayError) as excinfo:
        AnthropicProvider(factory).complete(make_request(), load_settings())

    assert_clean_error(excinfo.value, code)
    assert excinfo.value.status_code == status_code
    assert excinfo.value.request_id == f"req-test-{status_code}"


@pytest.mark.parametrize(
    "error, code",
    [
        pytest.param(anthropic.APITimeoutError(request=REQUEST), LLMErrorCode.TIMEOUT, id="timeout"),
        pytest.param(
            anthropic.APIConnectionError(message=PROVIDER_MESSAGE, request=REQUEST),
            LLMErrorCode.UNAVAILABLE,
            id="conexion",
        ),
        pytest.param(
            anthropic.APIResponseValidationError(
                httpx.Response(200, request=REQUEST), body=None, message=PROVIDER_MESSAGE
            ),
            LLMErrorCode.PROVIDER_ERROR,
            id="respuesta-no-valida",
        ),
        pytest.param(
            anthropic.AnthropicError(PROVIDER_MESSAGE), LLMErrorCode.PROVIDER_ERROR, id="otro"
        ),
    ],
)
def test_other_sdk_errors_are_converted(llm_env, error, code):
    factory = FakeClientFactory(error=error)

    with pytest.raises(LLMGatewayError) as excinfo:
        AnthropicProvider(factory).complete(make_request(), load_settings())

    assert_clean_error(excinfo.value, code)


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(
            FakeClientFactory(sdk_message(text_block("Respuesta inventada del modelo"))),
            id="correcta",
        ),
        pytest.param(
            FakeClientFactory(error=status_error(anthropic.BadRequestError, 400)), id="fallida"
        ),
    ],
)
def test_gateway_logs_contain_no_key_or_content(llm_env, caplog, factory):
    caplog.set_level(logging.INFO)
    gateway = LLMGateway(AnthropicProvider(factory))

    try:
        gateway.complete(make_request())
    except LLMGatewayError:
        pass

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "app.services.llm_gateway" in {record.name for record in caplog.records}
    for forbidden in (
        FAKE_API_KEY,
        SYSTEM,
        QUESTION,
        "Segunda pregunta inventada",
        "Respuesta inventada del modelo",
        "MENSAJE-DEL-PROVEEDOR",
    ):
        assert forbidden not in logged
