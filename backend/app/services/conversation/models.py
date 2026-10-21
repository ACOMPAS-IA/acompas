"""Contrato de la API de conversación (ACO-030, sección 8)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Límites de la petición (ficha ACO-030, P7).
MAX_DOCUMENTS = 3
MAX_DOCUMENT_CHARS = 30_000
MAX_MESSAGES = 21
MAX_QUESTION_CHARS = 2_000
MAX_ANSWER_CHARS = 8_000


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be empty")
    return value


class DocumentInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(max_length=MAX_DOCUMENT_CHARS)

    @field_validator("text")
    @classmethod
    def check_text(cls, value: str) -> str:
        return _require_text(value)


class ChatMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def check_content(cls, value: str) -> str:
        return _require_text(value)

    @model_validator(mode="after")
    def check_length(self) -> "ChatMessage":
        limit = MAX_QUESTION_CHARS if self.role == "user" else MAX_ANSWER_CHARS
        if len(self.content) > limit:
            raise ValueError(f"{self.role} content must have at most {limit} characters")
        return self


class ConversationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    documents: list[DocumentInput] = Field(min_length=1, max_length=MAX_DOCUMENTS)
    messages: list[ChatMessage] = Field(min_length=1, max_length=MAX_MESSAGES)

    @model_validator(mode="after")
    def check_turns(self) -> "ConversationRequest":
        # Empieza y termina en "user" y alterna: los pares son "user".
        for index, message in enumerate(self.messages):
            expected = "user" if index % 2 == 0 else "assistant"
            if message.role != expected:
                raise ValueError("messages must alternate user and assistant, starting with user")
        if self.messages[-1].role != "user":
            raise ValueError("last message must have role 'user'")
        return self


class ConversationResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    answer: str
    # El gateway informó stop_reason = "max_tokens".
    truncated: bool
