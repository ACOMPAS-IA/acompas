"""Validación del JWT emitido por Keycloak (ACO-014).

La validación se hace en dos fases para no confundir un token inválido con
una indisponibilidad del proveedor (ficha, sección 8.3):

1. se lee la cabecera y se resuelve la clave por `kid`;
2. se verifica la firma y los claims.

Un token inválido es siempre 401. El 503 se reserva a que el JWKS no se pueda
obtener o interpretar.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Protocol
from uuid import UUID

import jwt
from jwt import PyJWK, PyJWKClient, PyJWKSet
from jwt.exceptions import PyJWTError

from .config import CLIENT_ID, AuthSettings
from .errors import AuthError, AuthErrorCode
from .models import Principal

ALGORITHMS = ("RS256",)
REQUIRED_CLAIMS = ("exp", "iss", "sub", "typ")
APP_ROLES = frozenset({"paciente", "administrador"})

# Tiempo máximo para obtener el JWKS (ficha, sección 13: entre 5 y 10 s).
JWKS_TIMEOUT_SECONDS = 5
# Ventana de enfriamiento del refresco por `kid` desconocido: evita que un
# token con un `kid` inventado fuerce una descarga por petición.
JWKS_REFRESH_COOLDOWN_SECONDS = 30


class KeyProvider(Protocol):
    """Resuelve la clave de firma a partir del `kid` de la cabecera."""

    def get_verification_key(self, kid: str) -> Any: ...


def validate_token(
    token: str,
    settings: AuthSettings,
    key_provider: KeyProvider,
) -> Principal:
    """Valida el token y devuelve la identidad autenticada.

    Lanza `AuthError` con `INVALID_TOKEN` si el token no es válido y deja
    propagar `UNAVAILABLE` cuando el JWKS no está disponible.
    """
    try:
        header = jwt.get_unverified_header(token)
    except PyJWTError:
        raise AuthError(AuthErrorCode.INVALID_TOKEN) from None

    algorithm = header.get("alg")
    kid = header.get("kid")
    if algorithm not in ALGORITHMS or not isinstance(kid, str) or not kid:
        # Un algoritmo no permitido o sin `kid` no llega a consultar el JWKS.
        raise AuthError(AuthErrorCode.INVALID_TOKEN)

    key = key_provider.get_verification_key(kid)

    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=list(ALGORITHMS),
            issuer=settings.issuer,
            # El token de Keycloak lleva `aud: account`: la audiencia del
            # cliente se comprueba por `azp` (ficha, P3).
            options={"require": list(REQUIRED_CLAIMS), "verify_aud": False},
        )
    except PyJWTError:
        raise AuthError(AuthErrorCode.INVALID_TOKEN) from None

    return _principal(claims)


class JWKSClient:
    """Obtiene el JWKS y resuelve la clave por `kid`.

    Distingue por fase: los fallos al obtener o interpretar el JWKS son
    indisponibilidad (503); un `kid` que no está en un JWKS correcto es un
    token inválido (401).
    """

    def __init__(
        self,
        jwks_url: str,
        *,
        timeout: int = JWKS_TIMEOUT_SECONDS,
        refresh_cooldown: float = JWKS_REFRESH_COOLDOWN_SECONDS,
        client: Any | None = None,
    ) -> None:
        self._client = (
            client
            if client is not None
            else PyJWKClient(jwks_url, cache_jwk_set=True, timeout=timeout)
        )
        self._refresh_cooldown = refresh_cooldown
        self._last_refresh: float | None = None
        self._lock = threading.Lock()

    def get_verification_key(self, kid: str) -> Any:
        with self._lock:
            key_set = self._get_jwk_set(refresh=False)
            jwk = _find_signing_key(key_set, kid)
            if jwk is None and self._can_refresh():
                key_set = self._get_jwk_set(refresh=True)
                jwk = _find_signing_key(key_set, kid)
            if jwk is None:
                # El JWKS se ha obtenido y es utilizable: el token no es válido.
                raise AuthError(AuthErrorCode.INVALID_TOKEN)
            return jwk.key

    def _can_refresh(self) -> bool:
        if self._last_refresh is None:
            return True
        return time.monotonic() - self._last_refresh >= self._refresh_cooldown

    def _get_jwk_set(self, *, refresh: bool) -> PyJWKSet:
        if refresh:
            # Se registra el intento, no solo el éxito: un JWKS caído tampoco
            # puede provocar una descarga por petición.
            self._last_refresh = time.monotonic()
        try:
            key_set = self._client.get_jwk_set(refresh=refresh)
        except (PyJWTError, OSError, ValueError):
            # Incluye error de red, timeout, respuesta no JSON y JWKS malformado.
            raise AuthError(AuthErrorCode.UNAVAILABLE) from None
        if not _signing_keys(key_set):
            raise AuthError(AuthErrorCode.UNAVAILABLE)
        return key_set


def _signing_keys(key_set: PyJWKSet) -> list[PyJWK]:
    return [
        jwk
        for jwk in key_set.keys
        if jwk.public_key_use in ("sig", None) and jwk.key_id
    ]


def _find_signing_key(key_set: PyJWKSet, kid: str) -> PyJWK | None:
    for jwk in _signing_keys(key_set):
        if jwk.key_id == kid:
            return jwk
    return None


def _principal(claims: dict[str, Any]) -> Principal:
    if claims.get("typ") != "Bearer":
        raise AuthError(AuthErrorCode.INVALID_TOKEN)
    if claims.get("azp") != CLIENT_ID:
        raise AuthError(AuthErrorCode.INVALID_TOKEN)

    subject = claims.get("sub")
    try:
        user_id = UUID(subject)  # type: ignore[arg-type]
    except (AttributeError, TypeError, ValueError):
        raise AuthError(AuthErrorCode.INVALID_TOKEN) from None

    email = claims.get("email")
    return Principal(
        user_id=user_id,
        email=email if isinstance(email, str) and email else None,
        roles=_app_roles(claims),
    )


def _app_roles(claims: dict[str, Any]) -> frozenset[str]:
    realm_access = claims.get("realm_access")
    if not isinstance(realm_access, dict):
        return frozenset()
    roles = realm_access.get("roles")
    if not isinstance(roles, list):
        return frozenset()
    return frozenset(
        role for role in roles if isinstance(role, str) and role in APP_ROLES
    )
