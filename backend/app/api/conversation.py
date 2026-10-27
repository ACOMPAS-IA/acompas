"""Endpoint de conversación sobre documento (ACO-030).

La validación del JWT la añade ACO-014 a este router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.conversation import ConversationRequest, ConversationResponse, ConversationService
from app.services.llm_gateway import LLMErrorCode, LLMGateway, LLMGatewayError

router = APIRouter(prefix="/api")

# Código propio por error del gateway (ficha ACO-030, sección 8.3). Nunca se
# devuelve el mensaje del gateway, el código HTTP del proveedor ni el
# identificador de petición.
_HTTP_ERRORS = {
    LLMErrorCode.NOT_CONFIGURED: (503, "llm_not_configured"),
    LLMErrorCode.RATE_LIMIT: (503, "llm_busy"),
    LLMErrorCode.UNAVAILABLE: (503, "llm_unavailable"),
    LLMErrorCode.AUTH: (503, "llm_unavailable"),
    LLMErrorCode.TIMEOUT: (504, "llm_timeout"),
    LLMErrorCode.INVALID_REQUEST: (502, "llm_error"),
    LLMErrorCode.PROVIDER_ERROR: (502, "llm_error"),
}


def get_llm_gateway() -> LLMGateway:
    """Dependencia sustituible en los tests por un gateway con proveedor simulado."""
    return LLMGateway()


@router.post("/conversation", response_model=ConversationResponse)
def create_answer(
    request: ConversationRequest,
    gateway: Annotated[LLMGateway, Depends(get_llm_gateway)],
) -> ConversationResponse:
    try:
        return ConversationService(gateway).answer(request)
    except LLMGatewayError as error:
        status_code, detail = _HTTP_ERRORS[error.code]
        # Sin encadenar el error del gateway.
        raise HTTPException(status_code=status_code, detail=detail) from None
