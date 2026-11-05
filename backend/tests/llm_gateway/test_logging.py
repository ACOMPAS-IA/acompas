"""Registro del SDK y de la aplicación (ACO-028, ADR-015 §4)."""

import logging

import anthropic
import httpx2

from app.logging import configure_logging
from app.services.llm_gateway import LLMMessage, LLMRequest
from app.services.llm_gateway.anthropic_provider import AnthropicProvider
from app.services.llm_gateway.config import load_settings

from .conftest import FAKE_API_KEY

SYSTEM = "Prompt de sistema inventado para el registro"
QUESTION = "Pregunta inventada para el registro"
ANSWER = "Respuesta inventada que no debe registrarse"


def test_sdk_loggers_are_info_or_higher():
    configure_logging()

    for name in ("anthropic", "anthropic._base_client", "httpx2", "httpcore2"):
        logger = logging.getLogger(name)
        assert logger.getEffectiveLevel() >= logging.INFO
        assert logger.propagate is True


def test_configure_logging_is_idempotent():
    configure_logging()
    configure_logging()

    assert logging.getLogger("app").level == logging.INFO


def test_root_debug_does_not_log_content(llm_env, caplog):
    configure_logging()
    caplog.set_level(logging.DEBUG)

    def handler(request):
        return httpx2.Response(
            200,
            json={
                "id": "msg_test",
                "type": "message",
                "role": "assistant",
                "model": "modelo-que-responde",
                "content": [{"type": "text", "text": ANSWER}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 13, "output_tokens": 8},
            },
        )

    def factory(**kwargs):
        kwargs["http_client"] = anthropic.DefaultHttpxClient(
            trust_env=False, transport=httpx2.MockTransport(handler)
        )
        return anthropic.Anthropic(**kwargs)

    AnthropicProvider(factory).complete(
        LLMRequest(
            system=SYSTEM,
            messages=[LLMMessage(role="user", content=QUESTION)],
        ),
        load_settings(),
    )

    logged = "\n".join(record.getMessage() for record in caplog.records)
    for forbidden in (FAKE_API_KEY, SYSTEM, QUESTION, ANSWER):
        assert forbidden not in logged


def test_sdk_warning_propagates(caplog):
    configure_logging()
    caplog.set_level(logging.DEBUG)

    logging.getLogger("anthropic").warning("AVISO-SDK-DE-PRUEBA")

    assert "AVISO-SDK-DE-PRUEBA" in caplog.text
