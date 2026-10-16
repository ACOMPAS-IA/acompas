"""Configuración del LLM gateway (ACO-027, sección 8.4).

Se lee del entorno en cada llamada al gateway, no al importar el módulo.
"""

import os

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError

from .errors import LLMErrorCode, LLMGatewayError


class LLMSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    # SecretStr no muestra el valor al imprimir la configuración.
    api_key: SecretStr
    model: str = Field(min_length=1)
    max_output_tokens: int = Field(default=1024, gt=0)
    timeout_seconds: float = Field(default=60, gt=0)
    max_retries: int = Field(default=2, ge=0)


def _read_env(name: str) -> str | None:
    # Una variable vacía equivale a no definida.
    value = os.environ.get(name, "").strip()
    return value or None


def get_api_key() -> SecretStr | None:
    """Único punto que lee la clave del proveedor (ficha ACO-027, P7).

    ACO-028 o el ADR de secretos pueden cambiar aquí su origen sin tocar el
    resto del gateway.
    """
    value = _read_env("ANTHROPIC_API_KEY")
    return SecretStr(value) if value is not None else None


_OPTIONAL_FIELDS = {
    "LLM_MAX_OUTPUT_TOKENS": "max_output_tokens",
    "LLM_TIMEOUT_SECONDS": "timeout_seconds",
    "LLM_MAX_RETRIES": "max_retries",
}


def load_settings() -> LLMSettings:
    api_key = get_api_key()
    model = _read_env("LLM_MODEL")
    if api_key is None or model is None:
        raise LLMGatewayError(LLMErrorCode.NOT_CONFIGURED)

    values: dict[str, object] = {"api_key": api_key, "model": model}
    for variable, field in _OPTIONAL_FIELDS.items():
        value = _read_env(variable)
        if value is not None:
            values[field] = value

    error = None
    try:
        return LLMSettings(**values)
    except ValidationError:
        # Se lanza fuera del except para no encadenar la validación.
        error = LLMGatewayError(LLMErrorCode.NOT_CONFIGURED)
    raise error
