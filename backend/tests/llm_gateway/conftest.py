import os

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
    """Borra la configuración del gateway: los tests no dependen del contenedor.

    Incluye cualquier ANTHROPIC_* presente, no solo las cinco conocidas: la
    lista de permitidas de ACO-028 rechaza las demás.
    """
    names = {name for name in os.environ if name.startswith("ANTHROPIC_")}
    names.update(LLM_ENV_VARS)
    for name in names:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.fixture
def llm_env(no_llm_env):
    no_llm_env.setenv("ANTHROPIC_API_KEY", FAKE_API_KEY)
    no_llm_env.setenv("LLM_MODEL", FAKE_MODEL)
    return no_llm_env
