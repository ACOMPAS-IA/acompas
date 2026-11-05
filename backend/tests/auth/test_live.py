"""Comprobación manual del JWKS real (ACO-014, AC-01).

No corre en la CI: se ejecuta con Keycloak en marcha y `KEYCLOAK_LIVE=1`,
con `KEYCLOAK_ISSUER` y `KEYCLOAK_JWKS_URL` apuntando al realm local. No usa
usuarios ni tokens.
"""

import json
import os
import urllib.request

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("KEYCLOAK_LIVE") != "1",
    reason="requiere Keycloak local y KEYCLOAK_LIVE=1",
)


def _get_json(url: str):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def test_jwks_and_issuer_match_configuration():
    issuer = os.environ["KEYCLOAK_ISSUER"].rstrip("/")
    jwks_url = os.environ["KEYCLOAK_JWKS_URL"]

    discovery = _get_json(issuer + "/.well-known/openid-configuration")
    assert discovery["issuer"] == issuer

    key_set = _get_json(jwks_url)
    assert any(
        key.get("kty") == "RSA" and key.get("use") in (None, "sig")
        for key in key_set["keys"]
    )
