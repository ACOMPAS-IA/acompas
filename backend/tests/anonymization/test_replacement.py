"""Tests de etiquetas, numeración y sustitución (ACO-023, AC-11, AC-12)."""

import pytest

from app.services.anonymization.config import load_settings
from app.services.anonymization.detection import Detection
from app.services.anonymization.policy import Finding, select_findings
from app.services.anonymization.replacement import (
    assign_labels,
    count_entities,
    substitute,
)


def make(text, entity_type, fragment, occurrence=0, score=0.99):
    start = -1
    for _ in range(occurrence + 1):
        start = text.index(fragment, start + 1)
    return Finding(entity_type, start, start + len(fragment), score)


NON_PERSON_LABELS = [
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


@pytest.mark.parametrize("entity_type, fragment, expected", NON_PERSON_LABELS)
def test_non_person_labels(entity_type, fragment, expected):
    finding = make(fragment, entity_type, fragment)

    assert assign_labels(fragment, [finding]) == [expected]


def test_birth_date_label():
    text = "Fecha de nacimiento: 14/03/1958"
    finding = make(text, "DATE_TIME", "14/03/1958")

    assert assign_labels(text, [finding]) == ["[FECHA_NACIMIENTO]"]


def test_sanitarians_are_numbered_by_first_appearance():
    text = (
        "Dra. Inés Carrascal Ochoa. "
        "Dr. Andrés Lozoya Benítez. "
        "Firmado por Inés Carrascal Ochoa."
    )
    findings = [
        make(text, "PERSONAL_SANITARIO", "Inés Carrascal Ochoa", 0),
        make(text, "PERSONAL_SANITARIO", "Andrés Lozoya Benítez"),
        make(text, "PERSONAL_SANITARIO", "Inés Carrascal Ochoa", 1),
    ]

    assert assign_labels(text, findings) == [
        "[SANITARIO_1]",
        "[SANITARIO_2]",
        "[SANITARIO_1]",
    ]


def test_partial_mention_shares_the_patient_number():
    text = (
        "Paciente: Rosario Albendea Quintanar. "
        "Se informa a Albendea Quintanar."
    )
    findings = [
        make(text, "PACIENTE", "Rosario Albendea Quintanar"),
        make(text, "PACIENTE", "Albendea Quintanar"),
    ]

    assert assign_labels(text, findings) == ["[PACIENTE]", "[PACIENTE]"]


def test_distinct_patients_are_numbered():
    text = "Paciente: Rosario Albendea Quintanar. Acompañante: Inés Carrascal Ochoa."
    findings = [
        make(text, "PACIENTE", "Rosario Albendea Quintanar"),
        make(text, "PACIENTE", "Inés Carrascal Ochoa"),
    ]

    assert assign_labels(text, findings) == ["[PACIENTE_1]", "[PACIENTE_2]"]


def test_comma_split_name_is_one_patient_label():
    text = "Paciente: ALBENDEA QUINTANAR, ROSARIO"
    detections = [
        Detection("PACIENTE", text.index("ALBENDEA"), text.index("ALBENDEA") + 19, 0.99),
        Detection("PACIENTE", text.index("ROSARIO"), len(text), 0.99),
    ]

    findings = select_findings(text, detections, load_settings())

    assert assign_labels(text, findings) == ["[PACIENTE]"]


def test_family_roles_are_numbered():
    text = "Su marido, Tomás Ibarrola Senra, y su hija, Inés Carrascal Ochoa."
    findings = [
        make(text, "FAMILIAR", "Tomás Ibarrola Senra"),
        make(text, "FAMILIAR", "Inés Carrascal Ochoa"),
    ]

    assert assign_labels(text, findings) == ["[FAMILIAR_1]", "[FAMILIAR_2]"]


def test_substitution_replaces_values_and_keeps_the_rest():
    text = "Paciente: Rosario Albendea Quintanar. Teléfono: 600 123 456."
    findings = [
        make(text, "PACIENTE", "Rosario Albendea Quintanar"),
        make(text, "PHONE_NUMBER", "600 123 456"),
    ]
    labels = assign_labels(text, findings)

    result = substitute(text, findings, labels)

    assert result == "Paciente: [PACIENTE]. Teléfono: [TELEFONO]."
    assert "Rosario Albendea Quintanar" not in result
    assert "600 123 456" not in result


def test_repeated_mentions_get_the_same_label_and_are_replaced():
    text = (
        "Paciente: Rosario Albendea Quintanar. "
        "Rosario Albendea Quintanar firma el consentimiento."
    )
    findings = [
        make(text, "PACIENTE", "Rosario Albendea Quintanar", 0),
        make(text, "PACIENTE", "Rosario Albendea Quintanar", 1),
    ]
    labels = assign_labels(text, findings)

    result = substitute(text, findings, labels)

    assert labels == ["[PACIENTE]", "[PACIENTE]"]
    assert result.count("[PACIENTE]") == 2
    assert "Rosario Albendea Quintanar" not in result


def test_count_entities_counts_by_type():
    text = "Rosario Albendea Quintanar, 12345678Z y 600 123 456"
    findings = [
        make(text, "PACIENTE", "Rosario Albendea Quintanar"),
        make(text, "ES_DNI", "12345678Z"),
        make(text, "PHONE_NUMBER", "600 123 456"),
    ]

    assert count_entities(findings) == {
        "PACIENTE": 1,
        "ES_DNI": 1,
        "PHONE_NUMBER": 1,
    }
