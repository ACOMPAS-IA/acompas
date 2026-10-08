import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

from app.services.anonymization.analyzer import (
    REPLACED_PREDEFINED_RECOGNIZERS,
    build_analyzer,
)
from app.services.anonymization.detection import Detection, detect_entities
from app.services.anonymization.recognizers import HistoriaClinicaRecognizer

# Usan el modelo MEDDOCAN, como los tests de ACO-021.

FINDING_THRESHOLD = 0.35  # Umbral de hallazgo inicial (ADR-013, pendiente de aprobación).


@pytest.fixture(scope="module")
def analyzer():
    return build_analyzer()


@pytest.fixture(scope="module")
def historia_only_analyzer(analyzer):
    """Solo el reconocedor de historia, con el NLP real para el refuerzo por contexto.

    Aísla su puntuación de la del modelo, que también puede detectar el número.
    """
    registry = RecognizerRegistry(
        recognizers=[HistoriaClinicaRecognizer()], supported_languages=["es"]
    )
    return AnalyzerEngine(
        registry=registry, nlp_engine=analyzer.nlp_engine, supported_languages=["es"]
    )


def historia_score(engine, text, number="7300451"):
    scores = [
        result.score
        for result in engine.analyze(text=text, language="es", entities=["ES_HISTORIA_CLINICA"])
        if text[result.start : result.end] == number
    ]
    assert len(scores) == 1, scores
    return scores[0]


def fragments(text, detections, entity_type):
    return [
        (text[d.start : d.end], d.score) for d in detections if d.entity_type == entity_type
    ]


@pytest.mark.parametrize(
    "text",
    [
        "NHC: 7300451",
        "Número de historia: 7300451",
        "H.C.\n7300451",
    ],
)
def test_historia_clinica_context_raises_score(historia_only_analyzer, text):
    without_context = historia_score(
        historia_only_analyzer, "Se adjunta el resultado 7300451 al informe."
    )

    assert historia_score(historia_only_analyzer, text) > without_context


def test_historia_clinica_with_label_passes_finding_threshold(analyzer):
    text = "NHC: 7300451"
    detections = detect_entities(text, analyzer)

    assert any(
        fragment == "7300451" and score >= FINDING_THRESHOLD
        for fragment, score in fragments(text, detections, "ES_HISTORIA_CLINICA")
    )


@pytest.mark.parametrize(
    "text",
    [
        "Para pedir cita llame al 600123456 por la mañana.",
        "Código postal 47999 de la localidad.",
    ],
)
def test_phone_and_postal_code_are_not_historia_clinica(analyzer, text):
    detections = detect_entities(text, analyzer)

    assert all(
        score < FINDING_THRESHOLD
        for _, score in fragments(text, detections, "ES_HISTORIA_CLINICA")
    )


def test_dni_is_detected_with_exact_fragment(analyzer):
    # Si el modelo devuelve también ES_HISTORIA_CLINICA en el mismo sitio, se
    # conserva: resolver solapes es de ACO-023 (ficha ACO-022, sección 8.3).
    text = "DNI 12345678Z."
    detections = detect_entities(text, analyzer)

    assert "12345678Z" in [fragment for fragment, _ in fragments(text, detections, "ES_DNI")]


def test_detect_entities_returns_detections_without_role(analyzer):
    text = "Paciente: Rosario Albendea Quintanar. DNI: 12345678Z. NHC: 7300451."
    detections = detect_entities(text, analyzer)

    assert detections
    assert all(isinstance(d, Detection) and d.role is None for d in detections)
    for value in ["Rosario Albendea Quintanar", "12345678Z", "7300451"]:
        start = text.index(value)
        end = start + len(value)
        assert any(d.start <= start and end <= d.end for d in detections), value


def test_detect_entities_does_not_filter_by_score(analyzer):
    text = "Se adjunta el resultado 7300451 al informe."
    detections = detect_entities(text, analyzer)

    assert any(d.score < FINDING_THRESHOLD for d in detections)


def test_build_analyzer_replaces_predefined_spanish_id_recognizers(analyzer):
    names = {recognizer.name for recognizer in analyzer.registry.recognizers}

    assert {"DniRecognizer", "NieRecognizer", "HistoriaClinicaRecognizer"} <= names
    assert not names & set(REPLACED_PREDEFINED_RECOGNIZERS)
