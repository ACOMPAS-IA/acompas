"""Validación de firma y claims (ACO-014, AC-02 y AC-03)."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.services.auth import (
    AuthError,
    AuthErrorCode,
    AuthSettings,
    validate_token,
)

from .conftest import (
    CLIENT_ID,
    EMAIL,
    ISSUER,
    JWKS_URL,
    KID,
    USER_ID,
    FakeJWKSClient,
    make_token,
)

SETTINGS = AuthSettings(issuer=ISSUER, jwks_url=JWKS_URL)


def validate(token: str, signing_key):
    return validate_token(token, SETTINGS, FakeJWKSClient(signing_key.public_key()))


def test_valid_token_returns_principal(signing_key):
    principal = validate(make_token(signing_key), signing_key)

    assert principal.user_id == USER_ID
    assert principal.email == EMAIL
    assert principal.roles == frozenset({"paciente"})


def test_admin_role_is_read(signing_key):
    token = make_token(signing_key, realm_access={"roles": ["administrador"]})

    assert validate(token, signing_key).roles == frozenset({"administrador"})


def test_unknown_roles_are_ignored(signing_key):
    token = make_token(signing_key, realm_access={"roles": ["otro", "paciente"]})

    assert validate(token, signing_key).roles == frozenset({"paciente"})


def test_token_without_app_roles_keeps_empty_roles(signing_key):
    token = make_token(signing_key, realm_access={"roles": ["otro"]})

    assert validate(token, signing_key).roles == frozenset()


def test_email_is_optional(signing_key):
    token = make_token(signing_key, remove=("email",))

    assert validate(token, signing_key).email is None


def test_audience_is_not_validated(signing_key):
    # El token de Keycloak lleva `aud: account`; la audiencia se mira por `azp` (P3).
    token = make_token(signing_key, aud="otro-recurso")

    assert validate(token, signing_key).user_id == USER_ID


@pytest.mark.parametrize(
    "overrides, remove",
    [
        pytest.param(
            {"exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
            (),
            id="expired",
        ),
        pytest.param({"iss": "http://otro:8080/realms/acompas"}, (), id="wrong-issuer"),
        pytest.param({"azp": "otro-cliente"}, (), id="wrong-azp"),
        pytest.param({"typ": "ID"}, (), id="id-token"),
        pytest.param({"sub": "no-es-un-uuid"}, (), id="subject-not-uuid"),
        pytest.param({}, ("exp",), id="missing-exp"),
        pytest.param({}, ("iss",), id="missing-iss"),
        pytest.param({}, ("sub",), id="missing-sub"),
        pytest.param({}, ("typ",), id="missing-typ"),
    ],
)
def test_invalid_claims_are_rejected(signing_key, overrides, remove):
    token = make_token(signing_key, remove=remove, **overrides)

    with pytest.raises(AuthError) as error:
        validate(token, signing_key)

    assert error.value.code is AuthErrorCode.INVALID_TOKEN


def test_signature_from_another_key_is_rejected(signing_key, other_signing_key):
    token = make_token(other_signing_key)

    with pytest.raises(AuthError) as error:
        validate(token, signing_key)

    assert error.value.code is AuthErrorCode.INVALID_TOKEN


def test_malformed_token_is_rejected_without_asking_for_keys(signing_key):
    provider = FakeJWKSClient(signing_key.public_key())

    with pytest.raises(AuthError) as error:
        validate_token("no-es-un-jwt", SETTINGS, provider)

    assert error.value.code is AuthErrorCode.INVALID_TOKEN
    assert provider.kids == []


def test_algorithm_not_allowed_is_rejected_without_asking_for_keys(signing_key):
    now = datetime.now(timezone.utc)
    claims = {
        "iss": ISSUER,
        "azp": CLIENT_ID,
        "sub": str(USER_ID),
        "typ": "Bearer",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    token = jwt.encode(
        claims,
        "secreto-de-prueba-suficientemente-largo",
        algorithm="HS256",
        headers={"kid": KID},
    )
    provider = FakeJWKSClient(signing_key.public_key())

    with pytest.raises(AuthError) as error:
        validate_token(token, SETTINGS, provider)

    assert error.value.code is AuthErrorCode.INVALID_TOKEN
    assert provider.kids == []


def test_token_with_unknown_kid_is_invalid(signing_key):
    token = make_token(signing_key, kid="kid-desconocido")
    provider = FakeJWKSClient(
        signing_key.public_key(), error=AuthError(AuthErrorCode.INVALID_TOKEN)
    )

    with pytest.raises(AuthError) as error:
        validate_token(token, SETTINGS, provider)

    assert error.value.code is AuthErrorCode.INVALID_TOKEN
    assert provider.kids == ["kid-desconocido"]


def test_unavailable_jwks_is_propagated(signing_key):
    provider = FakeJWKSClient(
        signing_key.public_key(), error=AuthError(AuthErrorCode.UNAVAILABLE)
    )

    with pytest.raises(AuthError) as error:
        validate_token(make_token(signing_key), SETTINGS, provider)

    assert error.value.code is AuthErrorCode.UNAVAILABLE
