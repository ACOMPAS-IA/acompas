"""Tests de la política y los filtros (ACO-023, AC-02, AC-06 a AC-10)."""

import pytest

from app.services.anonymization.analyzer import DEFAULT_ENTITIES
from app.services.anonymization.config import load_settings
from app.services.anonymization.detection import Detection
from app.services.anonymization.policy import (
    POLICY,
    UnclassifiedEntityError,
    is_guaranteed,
    label_for,
    select_findings,
    unclassified_entities,
)


@pytest.fixture
def settings():
    return load_settings()


def detection(text, entity_type, fragment, score=0.99, occurrence=0):
    start = -1
    for _ in range(occurrence + 1):
        start = text.index(fragment, start + 1)
    return Detection(entity_type, start, start + len(fragment), score)


def select(text, detections, settings):
    return select_findings(text, detections, settings)


def fragments(text, findings):
    return [text[finding.start : finding.end] for finding in findings]


# --- Umbral de hallazgo -----------------------------------------------------


def test_finding_below_threshold_is_discarded(settings):
    text = "DNI: 12345678Z"
    below = detection(text, "ES_DNI", "12345678Z", max(0.0, settings.finding_threshold - 0.01))

    assert select(text, [below], settings) == []


def test_finding_above_threshold_is_anonymized(settings):
    text = "DNI: 12345678Z"
    above = detection(text, "ES_DNI", "12345678Z", settings.finding_threshold + 0.01)

    findings = select(text, [above], settings)

    assert [finding.entity_type for finding in findings] == ["ES_DNI"]


# --- Política por tipo ------------------------------------------------------


POLICY_CASES = [
    ("PACIENTE", "Rosario Albendea Quintanar", "[PACIENTE]"),
    ("PERSONAL_SANITARIO", "Inés Carrascal Ochoa", "[SANITARIO_n]"),
    ("FAMILIAR", "Tomás Ibarrola Senra", "[FAMILIAR_n]"),
    ("PERSON", "Fermín Ugarte Salcedo", "[PERSONA_n]"),
    ("ES_DNI", "12345678Z", "[DNI]"),
    ("ES_NIE", "X1234567L", "[NIE]"),
    ("ES_HISTORIA_CLINICA", "7300451", "[NHC]"),
    ("ID_ASEGURAMIENTO", "TSI 0000 1234 5678", "[ID_ASEGURAMIENTO]"),
    ("ID_CONTACTO_ASISTENCIAL", "Contacto 998877", "[ID_CONTACTO]"),
    ("ID_EMPLEO_PERSONAL_SANITARIO", "Empleado 445566", "[ID_EMPLEO]"),
    ("ID_TITULACION_PERSONAL_SANITARIO", "Colegiado 2828", "[ID_TITULACION]"),
    ("PHONE_NUMBER", "600 123 456", "[TELEFONO]"),
    ("EMAIL_ADDRESS", "rosario.albendea@example.com", "[EMAIL]"),
    ("CALLE", "Calle del Almendro Florido, 14", "[DIRECCION]"),
    ("HOSPITAL", "Hospital Universitario Monteluz", "[HOSPITAL]"),
    ("CENTRO_SALUD", "Centro de Salud Villaserena", "[CENTRO_SALUD]"),
    ("INSTITUCION", "Consejería de Sanidad", "[INSTITUCION]"),
    ("TERRITORIO", "Villaserena", "[TERRITORIO]"),
]


@pytest.mark.parametrize("entity_type, fragment, expected_label", POLICY_CASES)
def test_anonymized_types_use_the_documented_label(
    settings, entity_type, fragment, expected_label
):
    text = f"Dato: {fragment}."

    findings = select(text, [detection(text, entity_type, fragment)], settings)

    assert len(findings) == 1
    assert findings[0].entity_type == entity_type
    assert label_for(findings[0]) == expected_label
    assert is_guaranteed(findings[0]) is (entity_type not in {
        "HOSPITAL",
        "CENTRO_SALUD",
        "INSTITUCION",
        "TERRITORIO",
    })


@pytest.mark.parametrize(
    "entity_type, fragment",
    [
        ("AGE", "68 años"),
        ("SEXO", "Mujer"),
        ("PROFESION", "oncóloga"),
        ("PAIS", "España"),
        ("DATE_TIME", "12/09/2026"),
    ],
)
def test_context_types_are_not_anonymized(settings, entity_type, fragment):
    text = f"Dato: {fragment}."

    assert select(text, [detection(text, entity_type, fragment)], settings) == []


def test_every_default_entity_has_a_policy():
    assert unclassified_entities() == set()
    assert set(POLICY) == set(DEFAULT_ENTITIES)


def test_unknown_type_stops_processing(settings):
    text = "dato"

    with pytest.raises(UnclassifiedEntityError):
        select(text, [Detection("TIPO_DESCONOCIDO", 0, 4, 0.99)], settings)


# --- Fecha de nacimiento ----------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Fecha de nacimiento: 14/03/1958",
        "Fecha nac.: 14/03/1958",
        "F. nac. 14/03/1958",
        "F.NAC. 14/03/1958",
        "Nacimiento: 14/03/1958",
        "Nacido el 14/03/1958",
        "Nacida el 14/03/1958",
        "DOB: 14/03/1958",
    ],
)
def test_birth_date_with_cue_is_anonymized(settings, text):
    findings = select(text, [detection(text, "DATE_TIME", "14/03/1958")], settings)

    assert fragments(text, findings) == ["14/03/1958"]
    assert label_for(findings[0]) == "[FECHA_NACIMIENTO]"


@pytest.mark.parametrize(
    "text",
    [
        "Fecha: 14/03/1958",
        "Fecha del informe: 12/09/2026",
        "Consulta del 22 de septiembre de 2026",
    ],
)
def test_clinical_dates_are_kept(settings, text):
    fragment = "14/03/1958" if "14/03/1958" in text else text.split(": ")[-1]

    assert select(text, [detection(text, "DATE_TIME", fragment)], settings) == []


# --- Ruido y allow-list -----------------------------------------------------


@pytest.mark.parametrize(
    "entity_type, fragment",
    [
        ("PERSONAL_SANITARIO", ":"),
        ("DATE_TIME", ":"),
        ("PACIENTE", "Paciente"),
        ("PERSONAL_SANITARIO", "Dra."),
        ("FAMILIAR", "marido"),
        ("FAMILIAR", "esposa"),
    ],
)
def test_noise_fragments_are_discarded(settings, entity_type, fragment):
    text = f"{fragment} Rosario Albendea Quintanar"

    assert select(text, [detection(text, entity_type, fragment)], settings) == []


def test_fragment_with_a_name_is_not_noise(settings):
    text = "Paciente: Rosario,"
    findings = select(text, [detection(text, "PACIENTE", "Rosario,")], settings)

    assert fragments(text, findings) == ["Rosario,"]


@pytest.mark.parametrize(
    "term",
    [
        "CA 19-9",
        "CEA",
        "Ki-67",
        "BRCA2",
        "ADENOCARCINOMA",
        "CARCINOMA DUCTAL MODERADAMENTE DIFERENCIADO",
        "mFOLFIRINOX",
        "TAC",
    ],
)
def test_allow_listed_clinical_terms_are_kept(settings, term):
    text = f"Resultado: {term}."

    assert select(text, [detection(text, "PERSON", term)], settings) == []


def test_fragment_with_name_and_clinical_term_is_anonymized(settings):
    text = "CEA de Rosario Albendea"
    fragment = "CEA de Rosario Albendea"

    findings = select(text, [detection(text, "PERSON", fragment)], settings)

    assert fragments(text, findings) == [fragment]


# --- Solapes ----------------------------------------------------------------


def test_nested_overlap_keeps_the_winner_fragment(settings):
    text = "DNI: 12345678Z. Fecha del informe: 12/09/2026."
    dni = detection(text, "ES_DNI", "12345678Z", 1.0)
    historia = detection(text, "ES_HISTORIA_CLINICA", "12345678Z.", 0.618)

    findings = select(text, [dni, historia], settings)

    assert len(findings) == 1
    assert findings[0].entity_type == "ES_DNI"
    assert fragments(text, findings) == ["12345678Z"]


def test_partial_overlap_is_merged(settings):
    text = "abcdef"
    first = Detection("ES_DNI", 0, 4, 0.9)
    second = Detection("ES_HISTORIA_CLINICA", 2, 6, 0.5)

    findings = select(text, [first, second], settings)

    assert len(findings) == 1
    assert (findings[0].entity_type, findings[0].start, findings[0].end) == (
        "ES_DNI",
        0,
        6,
    )


def test_nested_overlap_with_text_is_united(settings):
    text = "12345678Z"
    outer = Detection("ES_HISTORIA_CLINICA", 0, len(text), 0.5)
    inner = Detection("ES_DNI", 0, 8, 0.9)

    findings = select(text, [outer, inner], settings)

    assert len(findings) == 1
    assert findings[0].entity_type == "ES_DNI"
    assert fragments(text, findings) == [text]


def test_guaranteed_category_wins_over_higher_unGuaranteed_score(settings):
    text = "Hospital Universitario Monteluz"
    hospital = detection(text, "HOSPITAL", text, 0.999)
    person = Detection("PERSON", 0, len(text), 0.9)

    findings = select(text, [person, hospital], settings)

    assert len(findings) == 1
    assert findings[0].entity_type == "PERSON"


def test_comma_split_name_is_one_person(settings):
    text = "Paciente: ALBENDEA QUINTANAR, ROSARIO"
    surname = detection(text, "PACIENTE", "ALBENDEA QUINTANAR,")
    name = detection(text, "PACIENTE", "ROSARIO")

    findings = select(text, [surname, name], settings)

    assert fragments(text, findings) == ["ALBENDEA QUINTANAR, ROSARIO"]


# --- Espacios, mutación y separación detección/decisión ---------------------


def test_surrounding_spaces_are_trimmed(settings):
    text = "Teléfono: 600 123 456\nFecha del informe: 12/09/2026."
    phone = detection(text, "PHONE_NUMBER", "600 123 456\n")

    findings = select(text, [phone], settings)

    assert fragments(text, findings) == ["600 123 456"]


def test_select_findings_does_not_mutate_detections(settings):
    text = "DNI: 12345678Z. Fecha de nacimiento: 14/03/1958."
    detections = [
        detection(text, "ES_DNI", "12345678Z"),
        detection(text, "DATE_TIME", "14/03/1958"),
    ]
    original = list(detections)

    select(text, detections, settings)

    assert detections == original
