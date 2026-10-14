import warnings

import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

from app.services.anonymization import analyzer as analyzer_module
from app.services.anonymization.analyzer import (
    DEFAULT_ENTITIES,
    MEDDOCAN_ENTITY_MAPPING,
    REPLACED_PREDEFINED_RECOGNIZERS,
    build_analyzer,
)
from app.services.anonymization.detection import (
    PERSON_TYPES,
    Detection,
    assign_roles,
    detect_entities,
)
from app.services.anonymization.recognizers import (
    HistoriaClinicaRecognizer,
    build_recognizers,
)

# Salvo los de asignación de rol y DEFAULT_ENTITIES, usan el modelo MEDDOCAN,
# como los tests de ACO-021.

FINDING_THRESHOLD = 0.35  # Umbral de hallazgo inicial (ADR-013).


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


def test_detect_entities_finds_each_identifier(analyzer):
    text = "Paciente: Rosario Albendea Quintanar. DNI: 12345678Z. NHC: 7300451."
    detections = detect_entities(text, analyzer)

    assert detections
    assert all(isinstance(d, Detection) for d in detections)
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

    assert {recognizer.name for recognizer in build_recognizers()} <= names
    assert not names & set(REPLACED_PREDEFINED_RECOGNIZERS)


def test_detect_entities_role_matches_entity_type(analyzer):
    text = "Paciente: Rosario Albendea Quintanar. Médico solicitante: Dra. Inés Carrascal Ochoa."
    detections = detect_entities(text, analyzer)

    assert any(d.role for d in detections)
    for d in detections:
        assert d.role == (d.entity_type if d.entity_type in PERSON_TYPES else None)


# Asignación de rol sin modelo: resultados construidos a mano (ficha ACO-022, P11).


def assign_one(text, name, entity_type, score=0.7):
    start = text.index(name)
    [detection] = assign_roles(text, [Detection(entity_type, start, start + len(name), score)])
    return detection


@pytest.mark.parametrize(
    "text, name, model_type, expected",
    [
        ("Comunicado a la Dra. Inés Carrascal Ochoa", "Inés Carrascal Ochoa", "PACIENTE", "PERSONAL_SANITARIO"),
        ("Paciente: Rosario Albendea Quintanar", "Rosario Albendea Quintanar", "PERSONAL_SANITARIO", "PACIENTE"),
        ("PACIENTE :\nRosario Albendea Quintanar", "Rosario Albendea Quintanar", "PERSON", "PACIENTE"),
        ("Solicitante : INÉS CARRASCAL OCHOA", "INÉS CARRASCAL OCHOA", "PERSON", "PERSONAL_SANITARIO"),
        ("Médico peticionario: Inés Carrascal Ochoa", "Inés Carrascal Ochoa", "PACIENTE", "PERSONAL_SANITARIO"),
        ("Fdo.: Andrés Lozoya Benítez", "Andrés Lozoya Benítez", "PERSON", "PERSONAL_SANITARIO"),
        ("Validado por: Fermín Ugarte Salcedo", "Fermín Ugarte Salcedo", "PERSON", "PERSONAL_SANITARIO"),
        ("(12/09/2026 13:45 - ANDRÉS LOZOYA BENÍTEZ)", "ANDRÉS LOZOYA BENÍTEZ", "PACIENTE", "PERSONAL_SANITARIO"),
    ],
)
def test_role_cue_overrides_model_type(text, name, model_type, expected):
    assert assign_one(text, name, model_type).entity_type == expected


@pytest.mark.parametrize(
    "text, name, model_type",
    [
        ("Se comenta con Fermín Ugarte Salcedo", "Fermín Ugarte Salcedo", "PERSON"),
        ("La paciente Rosario Albendea Quintanar acude", "Rosario Albendea Quintanar", "PERSON"),
        ("Acude con su marido, Tomás Ibarrola Senra", "Tomás Ibarrola Senra", "FAMILIAR"),
        # La pista solo vale para el nombre que va justo detrás.
        ("Dra. Inés Carrascal Ochoa y Fermín Ugarte Salcedo", "Fermín Ugarte Salcedo", "PERSON"),
    ],
)
def test_without_cue_model_type_is_kept(text, name, model_type):
    assert assign_one(text, name, model_type).entity_type == model_type


def test_role_assignment_ignores_non_person_detections():
    detection = assign_one("Paciente: 14/03/1958", "14/03/1958", "DATE_TIME")

    assert (detection.entity_type, detection.role) == ("DATE_TIME", None)


def test_role_assignment_keeps_positions_scores_and_detections():
    text = "Paciente: Rosario Albendea Quintanar. Dra. Inés Carrascal Ochoa. NHC: 7300451."
    detections = [
        Detection("PERSONAL_SANITARIO", 10, 36, 0.61),
        Detection("PACIENTE", 43, 63, 0.42),
        Detection("ES_HISTORIA_CLINICA", 70, 77, 0.3),
        Detection("PERSON", 10, 17, 0.2),
    ]

    assigned = assign_roles(text, detections)

    assert [(d.start, d.end, d.score) for d in assigned] == [
        (d.start, d.end, d.score) for d in detections
    ]
    assert [d.entity_type for d in assigned] == [
        "PACIENTE",
        "PERSONAL_SANITARIO",
        "ES_HISTORIA_CLINICA",
        "PACIENTE",
    ]


def test_role_is_derived_from_entity_type():
    text = "Paciente: Rosario Albendea Quintanar. Se comenta con Fermín Ugarte Salcedo el 12/09/2026."
    detections = [
        Detection("PERSONAL_SANITARIO", 10, 36, 0.9),
        Detection("PERSON", 53, 74, 0.9),
        Detection("DATE_TIME", 78, 88, 0.9),
    ]

    assert [(d.entity_type, d.role) for d in assign_roles(text, detections)] == [
        ("PACIENTE", "PACIENTE"),
        ("PERSON", "PERSON"),
        ("DATE_TIME", None),
    ]


# Separación entre detección y decisión (ficha ACO-022, AC-11).


def test_analyzer_defines_no_threshold():
    assert not [name for name in vars(analyzer_module) if "THRESHOLD" in name.upper()]


def test_default_entities_cover_model_and_recognizers():
    recognizer_entities = {
        entity for recognizer in build_recognizers() for entity in recognizer.supported_entities
    }

    assert set(MEDDOCAN_ENTITY_MAPPING.values()) <= set(DEFAULT_ENTITIES)
    assert recognizer_entities <= set(DEFAULT_ENTITIES)
    assert set(PERSON_TYPES) <= set(DEFAULT_ENTITIES)


# Indicador de acierto de rol (ficha ACO-022, AC-16 y B6). Informa, no bloquea.

ROLE_CASES = [
    ("C-01", "Paciente: Rosario Albendea Quintanar", "Rosario Albendea Quintanar", {"PACIENTE"}),
    (
        "C-02",
        "La paciente Rosario Albendea Quintanar acude a revisión.",
        "Rosario Albendea Quintanar",
        {"PACIENTE"},
    ),
    (
        "C-03",
        "Médico solicitante: Dra. Inés Carrascal Ochoa",
        "Inés Carrascal Ochoa",
        {"PERSONAL_SANITARIO"},
    ),
    (
        "C-04",
        "Solicitante : INÉS CARRASCAL OCHOA SERVICIO : ONCOLOGÍA MÉDICA",
        "INÉS CARRASCAL OCHOA",
        {"PERSONAL_SANITARIO"},
    ),
    (
        "C-05",
        "Validado por: Dr. Fermín Ugarte Salcedo",
        "Fermín Ugarte Salcedo",
        {"PERSONAL_SANITARIO"},
    ),
    (
        "C-06",
        "(12/09/2026 13:45 - ANDRÉS LOZOYA BENÍTEZ)",
        "ANDRÉS LOZOYA BENÍTEZ",
        {"PERSONAL_SANITARIO"},
    ),
    (
        "C-07",
        "El informe lo firma Andrés Lozoya Benítez, de Anatomía Patológica.",
        "Andrés Lozoya Benítez",
        {"PERSONAL_SANITARIO"},
    ),
    (
        "C-08",
        "Comité de tumores: Dra. Inés Carrascal Ochoa, Andrés Lozoya Benítez y Fermín Ugarte Salcedo.",
        "Fermín Ugarte Salcedo",
        {"PERSONAL_SANITARIO"},
    ),
    (
        "C-09",
        "Acude acompañada de su marido, Tomás Ibarrola Senra.",
        "Tomás Ibarrola Senra",
        {"FAMILIAR"},
    ),
    (
        "C-10",
        "Se informa del diagnóstico a su hijo, Tomás Ibarrola Senra, que la acompaña.",
        "Tomás Ibarrola Senra",
        {"FAMILIAR"},
    ),
    (
        "C-11",
        "ALBENDEA QUINTANAR, ROSARIO\nCaso: 99/00123\nEntidad: Hospital Universitario Monteluz",
        "ALBENDEA QUINTANAR, ROSARIO",
        {"PERSON", "PACIENTE"},
    ),
    ("C-12", "Persona de contacto: Tomás Ibarrola Senra", "Tomás Ibarrola Senra", {"PERSON"}),
]


def role_is_correct(text, name, expected, detections):
    """Acierta si todos los hallazgos de persona que contienen el nombre tienen un tipo esperado."""
    start = text.index(name)
    end = start + len(name)
    types = [
        d.entity_type
        for d in detections
        if d.entity_type in PERSON_TYPES and d.start <= start and end <= d.end
    ]
    return bool(types) and all(entity_type in expected for entity_type in types)


def test_role_accuracy_indicator(analyzer):
    failed = [
        case_id
        for case_id, text, name, expected in ROLE_CASES
        if not role_is_correct(text, name, expected, detect_entities(text, analyzer))
    ]
    correct = len(ROLE_CASES) - len(failed)

    # Solo los números de caso: el código no registra fragmentos del texto.
    warnings.warn(
        f"Acierto de rol: {100 * correct / len(ROLE_CASES):.0f} % "
        f"({correct}/{len(ROLE_CASES)}). Fallan: {', '.join(failed) or 'ninguno'}.",
        stacklevel=1,
    )
