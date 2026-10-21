"""Construcción de los mensajes para el gateway (ACO-030, sección 8.4)."""

import re

from app.services.llm_gateway import LLMMessage, LLMRequest
from app.services.prompts import DOCUMENT_CLOSE_TAG, DOCUMENT_OPEN_TAG

from .models import ConversationRequest

_NEUTRALIZED_TAG = "(documento_clinico)"

# Corchetes angulares normales, de ancho completo y de forma pequeña.
_OPENING = "<＜﹤"
_CLOSING = ">＞﹥"

# Toda aparición de una etiqueta de documento (ficha ACO-030, P6): con o sin
# barra (normal o de ancho completo), «documento» y «clinico» separados por
# guion bajo, guion o espacios, «clinico» con o sin tilde (también con la tilde
# combinada) y sin distinguir mayúsculas. Tras el nombre admite hasta 40
# caracteres de atributos sin corchetes angulares: una etiqueta sin cerrar no
# se lleva por delante el texto que la sigue.
_DOCUMENT_TAG = re.compile(
    rf"[{_OPENING}]\s*[/／]?\s*"
    r"documento[\s_-]+cl(?:[ií]́?)nico"
    rf"[^{_OPENING}{_CLOSING}]{{0,40}}"
    rf"[{_CLOSING}]",
    re.IGNORECASE,
)


def neutralize_delimiters(text: str) -> str:
    """Sustituye las etiquetas de documento por un texto que no las cierra ni las abre."""
    return _DOCUMENT_TAG.sub(_NEUTRALIZED_TAG, text)


def _first_user_content(request: ConversationRequest) -> str:
    documents = "\n\n".join(
        f"{DOCUMENT_OPEN_TAG}\n{neutralize_delimiters(document.text)}\n{DOCUMENT_CLOSE_TAG}"
        for document in request.documents
    )
    question = neutralize_delimiters(request.messages[0].content)
    return f"{documents}\n\n{question}"


def build_llm_request(request: ConversationRequest, system: str) -> LLMRequest:
    """Coloca los documentos en el primer mensaje y pasa el resto en orden.

    max_output_tokens no se envía: se usa el de la configuración del gateway.
    """
    messages = [LLMMessage(role="user", content=_first_user_content(request))]
    for message in request.messages[1:]:
        content = message.content
        if message.role == "user":
            content = neutralize_delimiters(content)
        messages.append(LLMMessage(role=message.role, content=content))
    return LLMRequest(system=system, messages=messages)
