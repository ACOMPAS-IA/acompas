"""Prueba con la API real (ficha ACO-027, P10).

Se omite salvo con ACOMPAS_LLM_LIVE=1, clave y modelo. No se ejecuta en CI: la
lanza el responsable a mano. Lee a propósito la configuración del contenedor.
"""

import os

import pytest

from app.services.llm_gateway import LLMGateway, LLMMessage, LLMRequest

pytestmark = pytest.mark.skipif(
    not (
        os.environ.get("ACOMPAS_LLM_LIVE") == "1"
        and os.environ.get("ANTHROPIC_API_KEY", "").strip()
        and os.environ.get("LLM_MODEL", "").strip()
    ),
    reason="prueba real: requiere ACOMPAS_LLM_LIVE=1, ANTHROPIC_API_KEY y LLM_MODEL",
)


def test_live_call():
    # Texto sintético corto, sin documento clínico.
    request = LLMRequest(
        system="Eres un asistente de pruebas. Responde en español con una sola frase breve.",
        messages=[
            LLMMessage(role="user", content="¿Qué es una analítica de sangre?"),
        ],
        max_output_tokens=200,
    )

    response = LLMGateway().complete(request)

    # Solo metadatos, para anotarlos en la PR.
    print(
        f"\nmodel={response.model} input_tokens={response.input_tokens} "
        f"output_tokens={response.output_tokens} stop_reason={response.stop_reason}"
    )
    assert response.text.strip()
    assert response.input_tokens > 0
    assert response.output_tokens > 0
