import pytest

from app.services.llm_gateway import LLMResponse

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

# Textos breves e inventados, con etiquetas de anonimización (ficha ACO-030, sección 9).
DOCUMENT_TEXT = "Informe inventado de [PACIENTE]. Firma [SANITARIO_1]. Marcador tumoral en rango."
QUESTION = "¿Qué quiere decir que el marcador está en rango?"
ANSWER = "Respuesta inventada del proveedor simulado."


class FakeProvider:
    """Proveedor simulado: registra las peticiones y devuelve una respuesta fija."""

    def __init__(self, text=ANSWER, stop_reason="end_turn", error=None):
        self.response = LLMResponse(
            text=text,
            model="modelo-que-responde",
            input_tokens=11,
            output_tokens=7,
            stop_reason=stop_reason,
        )
        self.error = error
        self.calls = []

    def complete(self, request, settings):
        self.calls.append(request)
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture
def no_llm_env(monkeypatch):
    """Borra las variables del gateway: los tests no dependen del contenedor."""
    for name in LLM_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.fixture
def llm_env(no_llm_env):
    no_llm_env.setenv("ANTHROPIC_API_KEY", FAKE_API_KEY)
    no_llm_env.setenv("LLM_MODEL", FAKE_MODEL)
    return no_llm_env
