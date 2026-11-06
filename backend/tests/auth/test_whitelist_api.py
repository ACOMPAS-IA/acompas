"""Contrato HTTP de la lista blanca (ACO-015, sección 11, puntos 4–13)."""

import logging
from datetime import datetime, timedelta, timezone

import pytest

from app.api.anonymization import get_anonymization_service
from app.main import app
from app.services.anonymization.models import (
    AnonymizationResult,
    AnonymizationStatus,
)

from .conftest import ANSWER, EMAIL, USER_ID, client, make_token, payload

CONVERSATION_URL = "/api/conversation"
ANONYMIZATION_URL = "/api/anonymization"
ANONYMIZATION_TEXT = "Informe inventado de [PACIENTE]."
OTHER_EMAIL = "otro@example.com"


class StubAnonymizationService:
    """Servicio simulado: no carga el modelo ni usa red."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def anonymize(self, text: str) -> AnonymizationResult:
        self.calls.append(text)
        return AnonymizationResult(
            status=AnonymizationStatus.VALIDADO,
            confidence=1.0,
            anonymized_text="[PACIENTE]",
            entities_count={"PACIENTE": 1},
        )


@pytest.fixture(autouse=True)
def auth(auth_env, jwks, gateway):
    """Configuración, clave fija y gateway simulado en las pruebas de API."""
    return jwks


@pytest.fixture
def anonymization_service():
    stub = StubAnonymizationService()
    app.dependency_overrides[get_anonymization_service] = lambda: stub
    yield stub
    app.dependency_overrides.pop(get_anonymization_service, None)


def headers_for(token: str | None = None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def post_conversation(token: str | None = None):
    return client.post(
        CONVERSATION_URL, json=payload(), headers=headers_for(token)
    )


def post_anonymization(token: str | None = None):
    return client.post(
        ANONYMIZATION_URL,
        json={"text": ANONYMIZATION_TEXT},
        headers=headers_for(token),
    )


def test_authorized_email_reaches_conversation(signing_key, gateway):
    response = post_conversation(make_token(signing_key))

    assert response.status_code == 200
    assert response.json() == {"answer": ANSWER, "truncated": False}
    assert len(gateway.calls) == 1


def test_authorized_email_reaches_anonymization(
    signing_key, anonymization_service
):
    response = post_anonymization(make_token(signing_key))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "validado"
    assert body["anonymized_text"] == "[PACIENTE]"
    assert anonymization_service.calls == [ANONYMIZATION_TEXT]


def test_email_outside_list_is_403_on_both_endpoints(
    signing_key, auth_env, gateway, anonymization_service
):
    auth_env.setenv("EMAILS_AUTORIZADOS", OTHER_EMAIL)
    token = make_token(signing_key)

    conversation = post_conversation(token)
    anonymization = post_anonymization(token)

    assert conversation.status_code == 403
    assert conversation.json() == {"detail": "forbidden"}
    assert anonymization.status_code == 403
    assert anonymization.json() == {"detail": "forbidden"}
    assert gateway.calls == []
    assert anonymization_service.calls == []


def test_token_without_email_is_403_on_both_endpoints(
    signing_key, gateway, anonymization_service
):
    token = make_token(signing_key, remove=("email",))

    assert post_conversation(token).status_code == 403
    assert post_anonymization(token).status_code == 403
    assert gateway.calls == []
    assert anonymization_service.calls == []


def test_empty_list_rejects_everyone(
    signing_key, auth_env, gateway, anonymization_service
):
    auth_env.setenv("EMAILS_AUTORIZADOS", "")
    token = make_token(signing_key)

    assert post_conversation(token).status_code == 403
    assert post_anonymization(token).status_code == 403
    assert gateway.calls == []
    assert anonymization_service.calls == []


def test_absent_list_rejects_everyone(
    signing_key, auth_env, gateway, anonymization_service
):
    auth_env.delenv("EMAILS_AUTORIZADOS", raising=False)
    token = make_token(signing_key)

    assert post_conversation(token).status_code == 403
    assert post_anonymization(token).status_code == 403
    assert gateway.calls == []
    assert anonymization_service.calls == []


def test_blank_entries_only_reject_everyone(
    signing_key, auth_env, gateway
):
    auth_env.setenv("EMAILS_AUTORIZADOS", " , ,, ")

    assert post_conversation(make_token(signing_key)).status_code == 403
    assert gateway.calls == []


@pytest.mark.parametrize(
    "configured, token_email",
    [
        pytest.param("  PACIENTE@EXAMPLE.COM ", EMAIL, id="list-upper-spaces"),
        pytest.param(EMAIL, "  Paciente@Example.Com ", id="token-upper-spaces"),
    ],
)
def test_case_and_spaces_are_normalized(
    signing_key, auth_env, configured, token_email
):
    auth_env.setenv("EMAILS_AUTORIZADOS", configured)

    response = post_conversation(make_token(signing_key, email=token_email))

    assert response.status_code == 200


def test_asterisk_is_literal_and_does_not_authorize(
    signing_key, auth_env
):
    auth_env.setenv("EMAILS_AUTORIZADOS", "*")

    assert post_conversation(make_token(signing_key)).status_code == 403


@pytest.mark.parametrize("configured", ["example.com", "paciente@example"])
def test_partial_or_domain_entry_does_not_authorize(
    signing_key, auth_env, configured
):
    auth_env.setenv("EMAILS_AUTORIZADOS", configured)

    assert post_conversation(make_token(signing_key)).status_code == 403


def test_withdrawal_cuts_access_on_next_request(signing_key, auth_env):
    token = make_token(signing_key)

    assert post_conversation(token).status_code == 200

    auth_env.setenv("EMAILS_AUTORIZADOS", OTHER_EMAIL)

    assert post_conversation(token).status_code == 403


def test_invalid_token_with_empty_list_is_still_401(signing_key, auth_env):
    auth_env.setenv("EMAILS_AUTORIZADOS", "")
    expired = make_token(
        signing_key, exp=datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    response = post_conversation(expired)

    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}


def test_rejection_does_not_expose_email_or_subject(
    signing_key, auth_env, caplog
):
    caplog.set_level(logging.DEBUG)
    auth_env.setenv("EMAILS_AUTORIZADOS", OTHER_EMAIL)
    token = make_token(signing_key)

    response = post_conversation(token)

    assert response.status_code == 403
    assert EMAIL not in response.text
    assert str(USER_ID) not in response.text
    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert EMAIL not in logged
    assert str(USER_ID) not in logged
    assert token not in logged
