"""Interfaz del proveedor LLM, sustituible por uno simulado en los tests."""

from typing import Protocol

from .config import LLMSettings
from .models import LLMRequest, LLMResponse


class LLMProvider(Protocol):
    def complete(self, request: LLMRequest, settings: LLMSettings) -> LLMResponse:
        """Llama al proveedor. Los fallos se lanzan como LLMGatewayError."""
        ...
