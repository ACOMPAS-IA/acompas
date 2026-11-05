"""Tests de la confianza del documento (ACO-023, AC-03)."""

import logging
from types import SimpleNamespace

import pytest

from app.services.anonymization import confidence as confidence_module
from app.services.anonymization.analyzer import get_token_pipeline
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


def test_contiguous_fragments_of_one_datum_use_the_best_support():
    findings = [
        finding("ES_HISTORIA_CLINICA", 0, 4, 0.95),
        finding("ES_HISTORIA_CLINICA", 4, 8, 0.55),
    ]

    assert document_confidence("12345678", findings, object()) == 0.95


def test_fragments_separated_only_by_spaces_are_one_datum():
    findings = [
        finding("ES_HISTORIA_CLINICA", 0, 4, 0.95),
        finding("ES_HISTORIA_CLINICA", 5, 9, 0.55),
    ]

    assert document_confidence("1234 5678", findings, object()) == 0.95


@pytest.mark.parametrize("separator", [" y ", "\n", ", "])
def test_two_distinct_data_of_one_category_use_the_weakest(separator):
    text = f"1234{separator}5678"
    findings = [
        finding("ES_HISTORIA_CLINICA", 0, 4, 0.95),
        finding("ES_HISTORIA_CLINICA", 4 + len(separator), 8 + len(separator), 0.55),
    ]

    assert document_confidence(text, findings, object()) == 0.55


def test_same_value_repeated_in_two_places_is_one_datum():
    text = "12345678Z y 12345678Z"
    findings = [
        finding("ES_DNI", 0, 9, 0.9),
        finding("ES_DNI", 12, 21, 0.6),
    ]

    assert document_confidence(text, findings, object()) == 0.9


def test_two_distinct_persons_use_the_weakest(monkeypatch):
    first = "Rosario Albendea Quintanar"
    second = "Inés Carrascal Ochoa"
    text = f"{first} y {second}"
    second_start = text.index(second)
    findings = [
        finding("PACIENTE", 0, len(first), 0.99),
        finding("PERSON", second_start, len(text), 0.99),
    ]
    monkeypatch.setattr(
        confidence_module,
        "_token_person_probabilities",
        lambda text, analyzer: [
            (0, len(first), 0.9),
            (second_start, len(text), 0.3),
        ],
    )

    # Dos personas distintas son dos datos: la débil rebaja la confianza.
    assert document_confidence(text, findings, object()) == 0.3


def test_repeated_mentions_of_the_same_person_use_the_best_support(monkeypatch):
    name = "Rosario Albendea Quintanar"
    text = f"{name} y {name}"
    second_start = text.index(name, 1)
    findings = [
        finding("PACIENTE", 0, len(name), 0.4),
        finding("PACIENTE", second_start, second_start + len(name), 0.5),
    ]
    monkeypatch.setattr(
        confidence_module,
        "_token_person_probabilities",
        lambda text, analyzer: [
            (0, len(name), 0.6),
            (second_start, second_start + len(name), 0.95),
        ],
    )

    assert document_confidence(text, findings, object()) == 0.95


def test_confidence_is_the_weakest_guaranteed_data(monkeypatch):
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


class _TokenComponent:
    def __init__(self):
        self.hf_pipeline = object()


def test_token_pipeline_is_found_by_attribute_not_by_component_name():
    # El nombre cambia entre versiones: en CI es `presidio_hf_token_pipe`.
    component = _TokenComponent()
    nlp = SimpleNamespace(
        pipeline=[("tok2vec", object()), ("presidio_hf_token_pipe", component)]
    )
    analyzer = SimpleNamespace(nlp_engine=SimpleNamespace(nlp={"es": nlp}))

    assert get_token_pipeline(analyzer) is component.hf_pipeline


def test_token_pipeline_is_found_in_the_pipe_bundled_with_presidio():
    # Presidio 2.2.366 sustituye HFTokenPipe por su propio componente, que
    # expone el pipeline en `pipeline` en lugar de `hf_pipeline`.
    pipeline = SimpleNamespace(tokenizer=object())
    component = SimpleNamespace(pipeline=pipeline)
    nlp = SimpleNamespace(
        pipeline=[("tok2vec", object()), ("presidio_hf_token_pipe", component)]
    )
    analyzer = SimpleNamespace(nlp_engine=SimpleNamespace(nlp={"es": nlp}))

    assert get_token_pipeline(analyzer) is pipeline


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
