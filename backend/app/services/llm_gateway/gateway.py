"""Punto único de paso hacia Claude API (ADR-006; ACO-027).

El control de gasto y el clasificador de intención se añadirán en
LLMGateway.complete(), posteriores al Sprint 1.
"""

import hashlib
import logging
import time

from .anthropic_provider import AnthropicProvider
from .config import load_settings
from .errors import LLMGatewayError
from .models import LLMRequest, LLMResponse
from .provider import LLMProvider

# Solo metadatos, nunca el contenido de prompts, mensajes ni respuestas (R-04).
logger = logging.getLogger("app.services.llm_gateway")


def _system_fingerprint(system: str) -> str:
    # Identifica la versión del prompt de ACO-029 sin registrar su texto.
    return hashlib.sha256(system.encode("utf-8")).hexdigest()[:12]


class LLMGateway:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider if provider is not None else AnthropicProvider()

    def complete(self, request: LLMRequest) -> LLMResponse:
        start = time.perf_counter()
        try:
            settings = load_settings()
            response = self._provider.complete(request, settings)
        except LLMGatewayError as error:
            logger.info(
                "llm_call_failed code=%s status_code=%s request_id=%s",
                error.code,
                error.status_code,
                error.request_id,
            )
            raise
        duration_ms = round((time.perf_counter() - start) * 1000)

        logger.info(
            "llm_call model=%s input_tokens=%d output_tokens=%d stop_reason=%s "
            "duration_ms=%d system_sha256=%s",
            response.model,
            response.input_tokens,
            response.output_tokens,
            response.stop_reason,
            duration_ms,
            _system_fingerprint(request.system),
        )
        return response
