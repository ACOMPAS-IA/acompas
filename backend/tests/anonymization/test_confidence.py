"""Tests de la confianza del documento (ACO-023, AC-03)."""

import logging

from app.services.anonymization import confidence as confidence_module
from app.services.anonymization.confidence import document_confidence
from app.services.anonymization.policy import Finding


def finding(entity_type, start, end, score):
    return Finding(entity_type=entity_type, start=start, end=end, score=score)


def person_tokens(text, probability):
    return [(0, len(text), probability)]


def test_document_without_guaranteed_categories_has_maximum_confidence():
    text = "Dieta blanda y abundante líquido."
    findings = [finding("HOSPITAL", 0, 5, 0.2)]

    assert document_confidence(text, findings, object()) == 1.0


def test_document_without_findings_has_maximum_confidence():
    assert document_confidence("texto", [], object()) == 1.0


def test_role_doubt_does_not_lower_confidence(monkeypatch):
    text = "Rosario Albendea Quintanar"
    findings = [finding("PACIENTE", 0, len(text), 0.4)]
    monkeypatch.setattr(
        confidence_module,
        "_token_person_probabilities",
        lambda text, analyzer: person_tokens(text, 0.92),
    )

    # La puntuación del hallazgo era 0,4; el soporte de las cuatro etiquetas
    # de persona es 0,92 y es lo que cuenta.
    assert document_confidence(text, findings, object()) == 0.92


def test_not_guaranteed_categories_do_not_lower_confidence():
    findings = [
        finding("ES_DNI", 0, 9, 0.95),
        finding("HOSPITAL", 10, 20, 0.1),
        finding("TERRITORIO", 21, 30, 0.2),
    ]

    assert document_confidence("texto de prueba", findings, object()) == 0.95


def test_fragments_of_one_category_use_the_best_support():
    findings = [
        finding("ES_HISTORIA_CLINICA", 0, 4, 0.95),
        finding("ES_HISTORIA_CLINICA", 5, 9, 0.55),
    ]

    assert document_confidence("texto de prueba", findings, object()) == 0.95


def test_confidence_is_the_weakest_guaranteed_category(monkeypatch):
    text = "Rosario Albendea Quintanar y 600 123 456"
    findings = [
        finding("PACIENTE", 0, 26, 0.99),
        finding("PHONE_NUMBER", 29, 40, 0.8),
    ]
    monkeypatch.setattr(
        confidence_module,
        "_token_person_probabilities",
        lambda text, analyzer: person_tokens(text, 0.99),
    )

    assert document_confidence(text, findings, object()) == 0.8


def test_degraded_mode_uses_the_finding_score_and_warns_without_content(monkeypatch, caplog):
    text = "Rosario Albendea Quintanar"
    findings = [finding("PACIENTE", 0, len(text), 0.77)]

    def fail(text, analyzer):
        raise RuntimeError("sin pipeline")

    monkeypatch.setattr(confidence_module, "_token_person_probabilities", fail)

    with caplog.at_level(logging.WARNING, logger="app.services.anonymization"):
        value = document_confidence(text, findings, object())

    assert value == 0.77
    assert "probabilidades por etiqueta" in caplog.text
    assert text not in caplog.text
