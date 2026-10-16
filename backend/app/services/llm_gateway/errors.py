"""Catálogo de errores del LLM gateway (ACO-027, sección 8.3)."""

from enum import StrEnum


class LLMErrorCode(StrEnum):
    NOT_CONFIGURED = "not_configured"
    AUTH = "auth"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"
    INVALID_REQUEST = "invalid_request"
    PROVIDER_ERROR = "provider_error"


# Mensaje fijo por código: nunca incluye la clave, el contenido de la petición
# ni el mensaje del proveedor (ficha ACO-027, P9).
_MESSAGES = {
    LLMErrorCode.NOT_CONFIGURED: "LLM gateway is not configured",
    LLMErrorCode.AUTH: "Claude API rejected the credentials",
    LLMErrorCode.RATE_LIMIT: "Claude API rate limit reached",
    LLMErrorCode.TIMEOUT: "Claude API call timed out",
    LLMErrorCode.UNAVAILABLE: "Claude API is unavailable",
    LLMErrorCode.INVALID_REQUEST: "Claude API rejected the request",
    LLMErrorCode.PROVIDER_ERROR: "Claude API returned an error",
}


class LLMGatewayError(Exception):
    def __init__(
        self,
        code: LLMErrorCode,
        *,
        status_code: int | None = None,
        request_id: str | None = None,
    ) -> None:
        self.code = code
        self.status_code = status_code
        self.request_id = request_id

        details = []
        if status_code is not None:
            details.append(f"HTTP {status_code}")
        if request_id is not None:
            details.append(f"request_id={request_id}")
        message = _MESSAGES[code]
        if details:
            message = f"{message} ({', '.join(details)})"
        super().__init__(message)
