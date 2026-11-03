"""Resolución de claves del JWKS (ACO-014, AC-06 y AC-07).

La distinción importante: un JWKS inaccesible o malformado es indisponibilidad
(503); un `kid` que no existe en un JWKS correcto es un token inválido (401).
"""

import json

import jwt
import pytest
from jwt import (
    PyJWKClientConnectionError,
    PyJWKClientError,
    PyJWKSet,
    PyJWKSetError,
)

from app.services.auth import AuthError, AuthErrorCode
from app.services.auth.tokens import JWKSClient

from .conftest import KID


def public_jwk(public_key, *, kid: str = KID, use: str = "sig") -> dict:
    data = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key))
    data.update({"kid": kid, "use": use, "alg": "RS256"})
    return data


def key_set(public_key, **kwargs) -> PyJWKSet:
    return PyJWKSet.from_dict({"keys": [public_jwk(public_key, **kwargs)]})


class StubJWKClient:
    """Sustituye a `PyJWKClient`: devuelve un JWKS fijo o lanza un error."""

    def __init__(self, jwk_set: PyJWKSet | None = None, error: Exception | None = None):
        self.jwk_set = jwk_set
        self.error = error
        self.refresh_calls = 0

    def get_jwk_set(self, refresh: bool = False) -> PyJWKSet:
        if refresh:
            self.refresh_calls += 1
        if self.error is not None:
            raise self.error
        return self.jwk_set


def build(stub: StubJWKClient) -> JWKSClient:
    return JWKSClient("http://no-se-usa", client=stub)


def test_known_kid_returns_its_key(signing_key):
    stub = StubJWKClient(key_set(signing_key.public_key()))

    key = build(stub).get_verification_key(KID)

    assert key.public_numbers() == signing_key.public_key().public_numbers()


def test_unknown_kid_is_invalid_token_and_refreshes_once(signing_key):
    stub = StubJWKClient(key_set(signing_key.public_key()))

    with pytest.raises(AuthError) as error:
        build(stub).get_verification_key("kid-desconocido")

    assert error.value.code is AuthErrorCode.INVALID_TOKEN
    assert stub.refresh_calls == 1


def test_unknown_kid_does_not_refresh_within_cooldown(signing_key):
    stub = StubJWKClient(key_set(signing_key.public_key()))
    client = build(stub)

    for kid in ("kid-uno", "kid-dos"):
        with pytest.raises(AuthError) as error:
            client.get_verification_key(kid)
        assert error.value.code is AuthErrorCode.INVALID_TOKEN

    assert stub.refresh_calls == 1


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(PyJWKClientConnectionError("sin conexión"), id="connection"),
        pytest.param(
            PyJWKClientError("The JWKS endpoint did not return a JSON object"),
            id="not-an-object",
        ),
        pytest.param(
            PyJWKSetError("The JWK Set did not contain any usable keys"),
            id="malformed-set",
        ),
        pytest.param(ValueError("Expecting value"), id="invalid-json"),
    ],
)
def test_jwks_failure_is_unavailable(signing_key, error):
    stub = StubJWKClient(error=error)

    with pytest.raises(AuthError) as auth_error:
        build(stub).get_verification_key(KID)

    assert auth_error.value.code is AuthErrorCode.UNAVAILABLE


def test_jwks_without_signing_keys_is_unavailable(signing_key):
    stub = StubJWKClient(key_set(signing_key.public_key(), use="enc"))

    with pytest.raises(AuthError) as error:
        build(stub).get_verification_key(KID)

    assert error.value.code is AuthErrorCode.UNAVAILABLE
