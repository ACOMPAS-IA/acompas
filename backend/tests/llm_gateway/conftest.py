import pytest

# Valores evidentemente falsos: no imitan el formato de una clave ni de un modelo reales.
FAKE_API_KEY = "clave-falsa-solo-para-tests"
FAKE_MODEL = "modelo-de-prueba"

LLM_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "LLM_MODEL",
    "LLM_MAX_OUTPUT_TOKENS",
    "LLM_TIMEOUT_SECONDS",
    "LLM_MAX_RETRIES",
)


@pytest.fixture
def no_llm_env(monkeypatch):
    """Borra las variables de la sección 8.4: los tests no dependen del contenedor."""
    for name in LLM_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.fixture
def llm_env(no_llm_env):
    no_llm_env.setenv("ANTHROPIC_API_KEY", FAKE_API_KEY)
    no_llm_env.setenv("LLM_MODEL", FAKE_MODEL)
    return no_llm_env
