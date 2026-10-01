from presidio_analyzer import AnalyzerEngine

from app.services.anonymization.analyzer import (
    DEFAULT_ENTITIES,
    MEDDOCAN_MODEL,
    build_analyzer,
)


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

    assert "PERSON" in entity_types
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
