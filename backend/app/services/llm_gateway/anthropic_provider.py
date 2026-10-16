"""Proveedor de Claude API. Único módulo de backend/app que importa anthropic (ADR-006)."""

from collections.abc import Callable

import anthropic

from .config import LLMSettings
from .errors import LLMErrorCode, LLMGatewayError
from .models import LLMRequest, LLMResponse

_INVALID_REQUEST_STATUSES = {400, 404, 413, 422}


def _status_code_to_error(status_code: int) -> LLMErrorCode:
    if status_code in (401, 403):
        return LLMErrorCode.AUTH
    if status_code == 408:
        return LLMErrorCode.TIMEOUT
    if status_code == 429:
        return LLMErrorCode.RATE_LIMIT
    if status_code in _INVALID_REQUEST_STATUSES:
        return LLMErrorCode.INVALID_REQUEST
    if status_code >= 500:
        return LLMErrorCode.UNAVAILABLE
    return LLMErrorCode.PROVIDER_ERROR


def _to_gateway_error(exc: anthropic.AnthropicError) -> LLMGatewayError:
    """Convierte un error del SDK sin conservar su mensaje (ficha ACO-027, P9)."""
    status_code = getattr(exc, "status_code", None)
    request_id = getattr(exc, "request_id", None)
    if not isinstance(status_code, int):
        status_code = None
    if not isinstance(request_id, str):
        request_id = None

    # APITimeoutError es subclase de APIConnectionError: va antes.
    if isinstance(exc, anthropic.APITimeoutError):
        code = LLMErrorCode.TIMEOUT
    elif isinstance(exc, anthropic.APIConnectionError):
        code = LLMErrorCode.UNAVAILABLE
    elif isinstance(exc, anthropic.APIStatusError):
        code = _status_code_to_error(exc.status_code)
    else:
        code = LLMErrorCode.PROVIDER_ERROR
    return LLMGatewayError(code, status_code=status_code, request_id=request_id)


class AnthropicProvider:
    def __init__(
        self, client_factory: Callable[..., anthropic.Anthropic] = anthropic.Anthropic
    ) -> None:
        self._client_factory = client_factory

    def complete(self, request: LLMRequest, settings: LLMSettings) -> LLMResponse:
        max_tokens = (
            request.max_output_tokens
            if request.max_output_tokens is not None
            else settings.max_output_tokens
        )

        error = None
        try:
            client = self._client_factory(
                api_key=settings.api_key.get_secret_value(),
                timeout=settings.timeout_seconds,
                max_retries=settings.max_retries,
            )
            response = client.messages.create(
                model=settings.model,
                system=request.system,
                messages=[
                    {"role": message.role, "content": message.content}
                    for message in request.messages
                ],
                max_tokens=max_tokens,
            )
        except anthropic.AnthropicError as exc:
            error = _to_gateway_error(exc)
        if error is not None:
            # Se lanza fuera del except para no encadenar la excepción original.
            raise error

        return LLMResponse(
            text="".join(
                block.text for block in response.content if block.type == "text"
            ),
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason,
        )
