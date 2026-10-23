"""Prueba del endpoint con la API real (ficha ACO-030, P11).

Se omite salvo con ACOMPAS_LLM_LIVE=1, clave y modelo. No se ejecuta en CI: la
lanza el responsable a mano. Lee a propósito la configuración del contenedor.
"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.prompts import load_system_prompt

pytestmark = pytest.mark.skipif(
    not (
        os.environ.get("ACOMPAS_LLM_LIVE") == "1"
        and os.environ.get("ANTHROPIC_API_KEY", "").strip()
        and os.environ.get("LLM_MODEL", "").strip()
    ),
    reason="prueba real: requiere ACOMPAS_LLM_LIVE=1, ANTHROPIC_API_KEY y LLM_MODEL",
)

# Texto sintético corto, inventado para esta prueba.
DOCUMENT = (
    "Analítica de [PACIENTE]. Solicitada por [SANITARIO_1]. "
    "Hemoglobina 13,1 g/dl (rango 12-16). CA 19-9 25 U/ml (rango 0-37)."
)


def test_live_conversation():
    prompt = load_system_prompt()

    response = TestClient(app).post(
        "/api/conversation",
        json={
            "documents": [{"text": DOCUMENT}],
            "messages": [{"role": "user", "content": "¿Qué es el CA 19-9?"}],
        },
    )

    # Solo metadatos, para anotarlos en la PR.
    print(f"\nprompt={prompt.version} sha256={prompt.sha256} status={response.status_code}")
    assert response.status_code == 200
    assert response.json()["answer"].strip()
