"""Contrato de entrada y salida del LLM gateway (ACO-027, sección 8)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _require_text(value: str) -> str:
    # La API rechaza también el texto que solo tiene espacios.
    if not value.strip():
        raise ValueError("must not be empty")
    return value


class LLMMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def check_content(cls, value: str) -> str:
        return _require_text(value)


class LLMRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    system: str
    messages: list[LLMMessage] = Field(min_length=1)
    # Sin valor, se usa el de la configuración (LLMSettings.max_output_tokens).
    max_output_tokens: int | None = Field(default=None, gt=0)

    @field_validator("system")
    @classmethod
    def check_system(cls, value: str) -> str:
        return _require_text(value)

    @model_validator(mode="after")
    def check_turns(self) -> "LLMRequest":
        if self.messages[0].role != "user" or self.messages[-1].role != "user":
            raise ValueError("first and last messages must have role 'user'")
        return self


class LLMResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    # Tal como lo informa el proveedor; quien llama decide qué hacer con él.
    stop_reason: str | None
