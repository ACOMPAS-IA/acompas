"""Configuración obligatoria de la validación (ACO-014, AC-01)."""

import pytest

from app.services.auth import AuthError, AuthErrorCode, load_settings

from .conftest import ISSUER, JWKS_URL


def test_settings_come_from_environment(auth_env):
    settings = load_settings()

    assert settings.issuer == ISSUER
    assert settings.jwks_url == JWKS_URL


@pytest.mark.parametrize("missing", ["KEYCLOAK_ISSUER", "KEYCLOAK_JWKS_URL"])
def test_missing_variable_is_unavailable(no_auth_env, missing):
    values = {"KEYCLOAK_ISSUER": ISSUER, "KEYCLOAK_JWKS_URL": JWKS_URL}
    for name, value in values.items():
        if name != missing:
            no_auth_env.setenv(name, value)

    with pytest.raises(AuthError) as error:
        load_settings()

    assert error.value.code is AuthErrorCode.UNAVAILABLE


def test_blank_value_is_unavailable(no_auth_env):
    no_auth_env.setenv("KEYCLOAK_ISSUER", "   ")
    no_auth_env.setenv("KEYCLOAK_JWKS_URL", JWKS_URL)

    with pytest.raises(AuthError) as error:
        load_settings()

    assert error.value.code is AuthErrorCode.UNAVAILABLE


def test_no_default_values_are_used(no_auth_env):
    with pytest.raises(AuthError) as error:
        load_settings()

    assert error.value.code is AuthErrorCode.UNAVAILABLE
