"""Tests de la configuración de umbrales (ACO-023, AC-01)."""

import pytest

from app.services.anonymization.config import (
    DEFAULT_DOCUMENT_THRESHOLD,
    DEFAULT_FINDING_THRESHOLD,
    DOCUMENT_THRESHOLD_ENV,
    FINDING_THRESHOLD_ENV,
    AnonymizationConfigurationError,
    load_settings,
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.delenv(FINDING_THRESHOLD_ENV, raising=False)
    monkeypatch.delenv(DOCUMENT_THRESHOLD_ENV, raising=False)


def test_defaults_when_variables_are_missing():
    settings = load_settings()

    assert settings.finding_threshold == DEFAULT_FINDING_THRESHOLD
    assert settings.document_threshold == DEFAULT_DOCUMENT_THRESHOLD


def test_defaults_when_variables_are_empty(monkeypatch):
    monkeypatch.setenv(FINDING_THRESHOLD_ENV, "")
    monkeypatch.setenv(DOCUMENT_THRESHOLD_ENV, "   ")

    settings = load_settings()

    assert settings.finding_threshold == DEFAULT_FINDING_THRESHOLD
    assert settings.document_threshold == DEFAULT_DOCUMENT_THRESHOLD


def test_reads_both_variables(monkeypatch):
    monkeypatch.setenv(FINDING_THRESHOLD_ENV, "0.4")
    monkeypatch.setenv(DOCUMENT_THRESHOLD_ENV, "0.6")

    settings = load_settings()

    assert settings.finding_threshold == 0.4
    assert settings.document_threshold == 0.6


@pytest.mark.parametrize("value", ["no-es-un-numero", "0,35"])
def test_rejects_non_numeric_value(monkeypatch, value):
    monkeypatch.setenv(FINDING_THRESHOLD_ENV, value)

    with pytest.raises(AnonymizationConfigurationError):
        load_settings()


@pytest.mark.parametrize("value", ["-0.1", "1.1"])
def test_rejects_out_of_range_value(monkeypatch, value):
    monkeypatch.setenv(DOCUMENT_THRESHOLD_ENV, value)

    with pytest.raises(AnonymizationConfigurationError):
        load_settings()


def test_rejects_finding_threshold_above_document_threshold(monkeypatch):
    monkeypatch.setenv(FINDING_THRESHOLD_ENV, "0.8")
    monkeypatch.setenv(DOCUMENT_THRESHOLD_ENV, "0.6")

    with pytest.raises(AnonymizationConfigurationError):
        load_settings()


def test_reads_environment_on_each_call(monkeypatch):
    monkeypatch.setenv(FINDING_THRESHOLD_ENV, "0.2")
    first = load_settings()

    monkeypatch.setenv(FINDING_THRESHOLD_ENV, "0.5")
    second = load_settings()

    assert first.finding_threshold == 0.2
    assert second.finding_threshold == 0.5
