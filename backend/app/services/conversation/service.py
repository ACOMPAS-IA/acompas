"""Conversación sobre documento (ACO-030).

Sin estado: no guarda ni registra nada de la conversación (R-04). El registro
de metadatos de cada llamada lo hace el gateway.
"""

from app.services.llm_gateway import LLMErrorCode, LLMGateway, LLMGatewayError
from app.services.prompts import load_system_prompt

from .messages import build_llm_request
from .models import ConversationRequest, ConversationResponse


class ConversationService:
    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway = gateway

    def answer(self, request: ConversationRequest) -> ConversationResponse:
        """Llama al gateway. Sus errores se propagan sin cambios."""
        llm_request = build_llm_request(request, load_system_prompt().text)
        response = self._gateway.complete(llm_request)
        if not response.text.strip():
            # Una respuesta vacía no sirve al paciente: se trata como error del proveedor.
            raise LLMGatewayError(LLMErrorCode.PROVIDER_ERROR)
        return ConversationResponse(
            answer=response.text,
            truncated=response.stop_reason == "max_tokens",
        )
