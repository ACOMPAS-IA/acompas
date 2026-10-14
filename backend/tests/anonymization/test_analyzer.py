from presidio_analyzer import AnalyzerEngine
from transformers import AutoConfig

from app.services.anonymization.analyzer import (
    DEFAULT_ENTITIES,
    MEDDOCAN_ENTITY_MAPPING,
    MEDDOCAN_MODEL,
    build_analyzer,
)
from app.services.anonymization.detection import PERSON_TYPES


def test_build_analyzer_returns_analyzer_engine():
    analyzer = build_analyzer()

    assert isinstance(analyzer, AnalyzerEngine)
    assert analyzer.supported_languages == ["es"]


def test_build_analyzer_uses_meddocan():
    analyzer = build_analyzer()

    assert analyzer.nlp_engine.models[0]["model_name"]["transformers"] == MEDDOCAN_MODEL


def test_analyzer_detects_entities_in_synthetic_spanish_clinical_text():
    analyzer = build_analyzer()

    text = (
        "Paciente Juan García. "
        "Fecha de consulta: 15/09/2026. "
        "Teléfono: 612345678."
    )

    results = analyzer.analyze(
        text=text,
        language="es",
        entities=DEFAULT_ENTITIES,
    )

    assert results

    entity_types = {result.entity_type for result in results}

    assert entity_types & set(PERSON_TYPES)
    assert "DATE_TIME" in entity_types
    assert "PHONE_NUMBER" in entity_types


def test_analyzer_results_have_valid_positions_and_scores():
    analyzer = build_analyzer()

    text = "Paciente Juan García, teléfono 612345678."

    results = analyzer.analyze(
        text=text,
        language="es",
        entities=DEFAULT_ENTITIES,
    )

    assert results

    for result in results:
        assert 0 <= result.start < result.end <= len(text)
        assert 0.0 <= result.score <= 1.0


def test_mapping_keys_match_model_labels():
    labels = AutoConfig.from_pretrained(MEDDOCAN_MODEL).id2label.values()
    model_entities = {label.split("-", 1)[1] for label in labels if label != "O"}

    assert set(MEDDOCAN_ENTITY_MAPPING) == model_entities


def test_mapping_keeps_person_roles():
    assert {
        key: value for key, value in MEDDOCAN_ENTITY_MAPPING.items() if value in PERSON_TYPES
    } == {
        "NOMBRE_SUJETO_ASISTENCIA": "PACIENTE",
        "NOMBRE_PERSONAL_SANITARIO": "PERSONAL_SANITARIO",
        "FAMILIARES_SUJETO_ASISTENCIA": "FAMILIAR",
        "OTROS_SUJETO_ASISTENCIA": "PERSON",
    }
