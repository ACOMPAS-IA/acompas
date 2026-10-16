import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.llm_gateway import LLMErrorCode, LLMGatewayError
from app.services.llm_gateway.config import get_api_key, load_settings

from .conftest import FAKE_API_KEY, FAKE_MODEL


def test_defaults(llm_env):
    settings = load_settings()

    assert settings.api_key.get_secret_value() == FAKE_API_KEY
    assert settings.model == FAKE_MODEL
    assert settings.max_output_tokens == 1024
    assert settings.timeout_seconds == 60
    assert settings.max_retries == 2


def test_custom_values(llm_env):
    llm_env.setenv("LLM_MAX_OUTPUT_TOKENS", "256")
    llm_env.setenv("LLM_TIMEOUT_SECONDS", "12.5")
    llm_env.setenv("LLM_MAX_RETRIES", "0")

    settings = load_settings()

    assert settings.max_output_tokens == 256
    assert settings.timeout_seconds == 12.5
    assert settings.max_retries == 0


def test_empty_optional_variables_use_defaults(llm_env):
    for name in ("LLM_MAX_OUTPUT_TOKENS", "LLM_TIMEOUT_SECONDS", "LLM_MAX_RETRIES"):
        llm_env.setenv(name, "")

    settings = load_settings()

    assert (settings.max_output_tokens, settings.timeout_seconds, settings.max_retries) == (
        1024,
        60,
        2,
    )


def assert_not_configured(excinfo):
    assert excinfo.value.code == LLMErrorCode.NOT_CONFIGURED
    assert excinfo.value.__cause__ is None
    assert excinfo.value.__context__ is None
    assert FAKE_API_KEY not in str(excinfo.value)


@pytest.mark.parametrize("missing", ["ANTHROPIC_API_KEY", "LLM_MODEL"])
@pytest.mark.parametrize("how", ["delete", "empty"])
def test_missing_required_variable(llm_env, missing, how):
    if how == "delete":
        llm_env.delenv(missing)
    else:
        llm_env.setenv(missing, "")

    with pytest.raises(LLMGatewayError) as excinfo:
        load_settings()

    assert_not_configured(excinfo)


@pytest.mark.parametrize(
    "variable, value",
    [
        ("LLM_MAX_OUTPUT_TOKENS", "abc"),
        ("LLM_MAX_OUTPUT_TOKENS", "0"),
        ("LLM_MAX_OUTPUT_TOKENS", "1.5"),
        ("LLM_TIMEOUT_SECONDS", "0"),
        ("LLM_TIMEOUT_SECONDS", "-1"),
        ("LLM_TIMEOUT_SECONDS", "rápido"),
        ("LLM_MAX_RETRIES", "-1"),
        ("LLM_MAX_RETRIES", "dos"),
    ],
)
def test_invalid_number(llm_env, variable, value):
    llm_env.setenv(variable, value)

    with pytest.raises(LLMGatewayError) as excinfo:
        load_settings()

    assert_not_configured(excinfo)


def test_get_api_key(no_llm_env):
    assert get_api_key() is None

    no_llm_env.setenv("ANTHROPIC_API_KEY", "")
    assert get_api_key() is None

    no_llm_env.setenv("ANTHROPIC_API_KEY", FAKE_API_KEY)
    assert get_api_key().get_secret_value() == FAKE_API_KEY


def test_settings_representation_hides_key(llm_env):
    settings = load_settings()

    for text in (repr(settings), str(settings), f"{settings}", repr(settings.api_key)):
        assert FAKE_API_KEY not in text


def test_health_without_llm_configuration(no_llm_env):
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
