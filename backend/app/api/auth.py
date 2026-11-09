"""Dependencia de autenticación del API (ACO-014 y ACO-015).

Traduce los errores de la validación a las respuestas de las fichas (ACO-014,
sección 8.3; ACO-015, sección 8). El cuerpo nunca incluye el token, el email,
el ``sub`` ni el motivo concreto del rechazo.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth import (
    AuthError,
    AuthErrorCode,
    AuthSettings,
    JWKSClient,
    Principal,
    is_email_authorized,
    load_authorized_emails,
    load_settings,
    validate_token,
)

bearer_scheme = HTTPBearer(auto_error=False)

_HTTP_ERRORS = {
    AuthErrorCode.INVALID_TOKEN: (401, "unauthorized"),
    AuthErrorCode.FORBIDDEN: (403, "forbidden"),
    AuthErrorCode.UNAVAILABLE: (503, "auth_unavailable"),
}


def _http_error(code: AuthErrorCode) -> HTTPException:
    status_code, detail = _HTTP_ERRORS[code]
    headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
    return HTTPException(status_code=status_code, detail=detail, headers=headers)


def get_auth_settings() -> AuthSettings:
    try:
        return load_settings()
    except AuthError as error:
        raise _http_error(error.code) from None


@lru_cache(maxsize=8)
def _build_jwks_client(jwks_url: str) -> JWKSClient:
    # La caché de claves vive en el cliente: se reutiliza entre peticiones.
    return JWKSClient(jwks_url)


def get_jwks_client(
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> JWKSClient:
    """Dependencia sustituible en los tests por un cliente con clave fija."""
    return _build_jwks_client(settings.jwks_url)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    jwks_client: Annotated[JWKSClient, Depends(get_jwks_client)],
) -> Principal:
    if credentials is None:
        raise _http_error(AuthErrorCode.INVALID_TOKEN)

    try:
        principal = validate_token(credentials.credentials, settings, jwks_client)
    except AuthError as error:
        raise _http_error(error.code) from None

    if not principal.roles:
        # Autenticado, pero sin ninguno de los roles de aplicación (P4).
        raise _http_error(AuthErrorCode.FORBIDDEN)

    # La lista se lee en cada petición: retirar un email corta el acceso en la
    # petición siguiente. Ausente o vacía se cierra por defecto (ACO-015).
    if not is_email_authorized(principal.email, load_authorized_emails()):
        raise _http_error(AuthErrorCode.FORBIDDEN)
    return principal
