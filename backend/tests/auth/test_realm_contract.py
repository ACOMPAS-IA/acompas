"""Coherencia con el realm de Keycloak (ACO-014, AC-09).

El test solo lee el JSON del realm: no levanta Keycloak ni necesita red.
"""

import json
from pathlib import Path

import pytest

from app.services.auth import CLIENT_ID

REALM_PATH = (
    Path(__file__).resolve().parents[3]
    / "infra"
    / "keycloak"
    / "import"
    / "acompas-realm.json"
)

pytestmark = pytest.mark.skipif(
    not REALM_PATH.is_file(),
    reason="el JSON del realm no está en la imagen del backend",
)


@pytest.fixture(scope="module")
def realm() -> dict:
    return json.loads(REALM_PATH.read_text(encoding="utf-8"))


def test_realm_name(realm):
    assert realm["realm"] == "acompas"


def test_client_matches_backend(realm):
    clients = [
        client for client in realm["clients"] if client.get("clientId") == CLIENT_ID
    ]

    assert len(clients) == 1
    client = clients[0]
    assert client["publicClient"] is True
    assert client["standardFlowEnabled"] is True
    assert "roles" in client["defaultClientScopes"]
    assert "email" in client["defaultClientScopes"]


def test_application_roles_exist(realm):
    roles = {role["name"] for role in realm["roles"]["realm"]}

    assert {"paciente", "administrador"} <= roles
