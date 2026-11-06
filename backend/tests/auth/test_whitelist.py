"""Tests unitarios de la lista blanca (ACO-015, sección 11, puntos 1–3)."""

import logging

from app.services.auth.whitelist import (
    is_email_authorized,
    load_authorized_emails,
    log_whitelist_summary,
    parse_authorized_emails,
)


def test_missing_or_empty_configuration_is_empty_list():
    assert parse_authorized_emails(None) == frozenset()
    assert parse_authorized_emails("") == frozenset()
    assert parse_authorized_emails("   ") == frozenset()
    assert parse_authorized_emails(" , ,, ") == frozenset()


def test_parse_trims_lowercases_and_discards_empty_entries():
    parsed = parse_authorized_emails(
        "  Paciente@Example.COM ,, OTRO@EXAMPLE.COM  , "
    )

    assert parsed == frozenset({"paciente@example.com", "otro@example.com"})


def test_parse_counts_distinct_normalized_addresses():
    parsed = parse_authorized_emails(
        "paciente@example.com,PACIENTE@example.com, paciente@example.com"
    )

    assert parsed == frozenset({"paciente@example.com"})


def test_load_reads_environment_on_each_call(monkeypatch):
    monkeypatch.setenv("EMAILS_AUTORIZADOS", "primero@example.com")
    assert load_authorized_emails() == frozenset({"primero@example.com"})

    monkeypatch.setenv("EMAILS_AUTORIZADOS", "segundo@example.com")
    assert load_authorized_emails() == frozenset({"segundo@example.com"})

    monkeypatch.delenv("EMAILS_AUTORIZADOS", raising=False)
    assert load_authorized_emails() == frozenset()


def test_authorized_email_matches_case_and_outer_spaces():
    authorized = frozenset({"paciente@example.com"})

    assert is_email_authorized("paciente@example.com", authorized)
    assert is_email_authorized("  PACIENTE@EXAMPLE.COM  ", authorized)


def test_email_outside_list_is_not_authorized():
    authorized = frozenset({"paciente@example.com"})

    assert not is_email_authorized("otro@example.com", authorized)


def test_absent_or_blank_email_is_not_authorized():
    authorized = frozenset({"paciente@example.com", ""})

    assert not is_email_authorized(None, authorized)
    assert not is_email_authorized("", authorized)
    assert not is_email_authorized("   ", authorized)


def test_asterisk_is_literal_and_does_not_match_normal_email():
    authorized = frozenset({"*"})

    assert not is_email_authorized("paciente@example.com", authorized)
    assert is_email_authorized("*", authorized)


def test_no_partial_or_domain_matching():
    assert not is_email_authorized(
        "paciente@example.com", frozenset({"example.com"})
    )
    assert not is_email_authorized(
        "paciente@example.com", frozenset({"paciente@example"})
    )
    assert not is_email_authorized(
        "otro-paciente@example.com", frozenset({"paciente@example.com"})
    )


def test_startup_summary_logs_count_but_not_values(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setenv(
        "EMAILS_AUTORIZADOS",
        "paciente@example.com, OTRO@example.com,paciente@example.com",
    )

    log_whitelist_summary()

    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "2 direcciones autorizadas" in messages
    assert "paciente@example.com" not in messages
    assert "otro@example.com" not in messages


def test_startup_summary_reports_zero_on_empty_list(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.delenv("EMAILS_AUTORIZADOS", raising=False)

    log_whitelist_summary()

    errors = [
        record for record in caplog.records if record.levelno >= logging.ERROR
    ]
    assert errors
    assert "0 direcciones autorizadas" in errors[0].getMessage()


def test_startup_summary_reports_zero_on_blank_list(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setenv("EMAILS_AUTORIZADOS", " ,  ")

    log_whitelist_summary()

    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "0 direcciones autorizadas" in messages
