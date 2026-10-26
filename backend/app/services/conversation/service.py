"""Conversación sobre documento (ACO-030).

Sin estado: no guarda ni registra nada de la conversación (R-04). El registro
de metadatos de cada llamada lo hace el gateway.
"""

from app.services.llm_gateway import LLMErrorCode, LLMGateway, LLMGatewayError
from app.services.prompts import load_system_prompt

from .messages import build_llm_request
from .models import MAX_ANSWER_CHARS, ConversationRequest, ConversationResponse


class ConversationService:
    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway = gateway

    def answer(self, request: ConversationRequest) -> ConversationResponse:
        """Llama al gateway. Sus errores se propagan sin cambios."""
        llm_request = build_llm_request(request, load_system_prompt().text)
        response = self._gateway.complete(llm_request)
        # Tope duro (ficha ACO-030, P7): una respuesta devuelta siempre se puede reenviar.
        answer = response.text[:MAX_ANSWER_CHARS]
        if not answer.strip():
            # Una respuesta vacía no sirve al paciente: se trata como error del proveedor.
            raise LLMGatewayError(LLMErrorCode.PROVIDER_ERROR)
        return ConversationResponse(
            answer=answer,
            truncated=response.stop_reason == "max_tokens" or len(response.text) > MAX_ANSWER_CHARS,
        )
