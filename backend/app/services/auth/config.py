"""Configuración de la validación del JWT (ACO-014, P2 y P7).

Se lee del entorno en cada petición, no al importar el módulo, para que un
cambio de configuración no exija reiniciar el proceso y para que los tests
puedan ajustarla. Sin valores por defecto: los valores locales viven en
`docker-compose.yml` y `.env.example`.
"""

import os

from pydantic import BaseModel, ConfigDict, ValidationError

from .errors import AuthError, AuthErrorCode

ISSUER_ENV = "KEYCLOAK_ISSUER"
JWKS_URL_ENV = "KEYCLOAK_JWKS_URL"

# Cliente OIDC de la aplicación (ACO-013). No es configurable.
CLIENT_ID = "acompas-frontend"


class AuthSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    issuer: str
    jwks_url: str


def _read_env(name: str) -> str | None:
    # Una variable vacía equivale a no definida.
    value = os.environ.get(name, "").strip()
    return value or None


def load_settings() -> AuthSettings:
    """Devuelve la configuración vigente.

    Sin emisor o sin JWKS no se puede autenticar a nadie: el fallo se trata
    como indisponibilidad (503), no como token inválido.
    """
    issuer = _read_env(ISSUER_ENV)
    jwks_url = _read_env(JWKS_URL_ENV)
    if issuer is None or jwks_url is None:
        raise AuthError(AuthErrorCode.UNAVAILABLE)

    error = None
    try:
        return AuthSettings(issuer=issuer, jwks_url=jwks_url)
    except ValidationError:
        # Se lanza fuera del except para no encadenar la validación.
        error = AuthError(AuthErrorCode.UNAVAILABLE)
    raise error
