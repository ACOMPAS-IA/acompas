"""Errores de la validación del JWT (ACO-014).

El código distingue las tres respuestas del contrato (sección 8.3): token
inválido, token válido sin rol y autenticación no disponible.
"""

from enum import StrEnum


class AuthErrorCode(StrEnum):
    INVALID_TOKEN = "invalid_token"
    FORBIDDEN = "forbidden"
    UNAVAILABLE = "unavailable"


class AuthError(Exception):
    """Error de autenticación que el API traduce a un código HTTP."""

    def __init__(self, code: AuthErrorCode) -> None:
        super().__init__(code.value)
        self.code = code
