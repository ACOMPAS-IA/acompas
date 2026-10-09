import pytest

from app.services.anonymization.recognizers import (
    HISTORIA_CLINICA_BASE_SCORE,
    LABELED_ENTITY_SCORE,
    SURNAMES_FIRST_BASE_SCORE,
    ApellidosNombreRecognizer,
    DniRecognizer,
    DomicilioRecognizer,
    FirmaFechadaRecognizer,
    HistoriaClinicaRecognizer,
    NieRecognizer,
    NombreTrasEtiquetaRecognizer,
)

# Sin modelo ni red: se usa cada reconocedor aislado, sin refuerzo por contexto.

FINDING_THRESHOLD = 0.35  # Umbral de hallazgo inicial (ADR-013).


def find(recognizer, text):
    return [
        (text[result.start : result.end], result.score)
        for result in recognizer.analyze(
            text=text, entities=recognizer.supported_entities, nlp_artifacts=None
        )
    ]


def find_typed(recognizer, text):
    return [
        (text[result.start : result.end], result.entity_type, result.score)
        for result in recognizer.analyze(
            text=text, entities=recognizer.supported_entities, nlp_artifacts=None
        )
    ]


def paciente_recognizer():
    return NombreTrasEtiquetaRecognizer("Paciente", "PACIENTE", "NombreTrasPacienteRecognizer")


def solicitante_recognizer():
    return NombreTrasEtiquetaRecognizer(
        "Solicitante", "PERSONAL_SANITARIO", "NombreTrasSolicitanteRecognizer"
    )


@pytest.mark.parametrize("dni", ["12345678Z", "87654321X", "00000000T"])
def test_dni_with_valid_letter_gets_max_score(dni):
    assert find(DniRecognizer(), f"DNI: {dni}") == [(dni, 1.0)]


def test_dni_with_invalid_letter_is_kept_with_lower_score():
    results = find(DniRecognizer(), "DNI: 12345678A")

    assert len(results) == 1
    text, score = results[0]
    assert text == "12345678A"
    assert 0 < score < 1.0


def test_dni_letter_in_lowercase_is_validated():
    assert find(DniRecognizer(), "DNI: 12345678z") == [("12345678z", 1.0)]


def test_dni_is_not_found_inside_longer_tokens():
    assert find(DniRecognizer(), "Ref. A12345678Z y 123456789Z") == []


@pytest.mark.parametrize("dni", ["12345678-Z", "12345678 Z", "12.345.678-Z"])
def test_dni_with_separators_and_valid_letter_gets_max_score(dni):
    assert find(DniRecognizer(), f"DNI: {dni}.") == [(dni, 1.0)]


@pytest.mark.parametrize("dni", ["12345678-A", "12345678 A", "12.345.678-A"])
def test_dni_with_separators_and_invalid_letter_is_kept_with_lower_score(dni):
    results = find(DniRecognizer(), f"DNI: {dni}.")

    assert len(results) == 1
    text, score = results[0]
    assert text == dni
    assert 0 < score < 1.0


def test_dni_with_space_needs_uppercase_letter():
    assert find(DniRecognizer(), "Se registraron 12345678 y otros valores") == []


def test_nie_with_valid_letter_gets_max_score():
    assert find(NieRecognizer(), "NIE: X1234567L") == [("X1234567L", 1.0)]


def test_nie_with_invalid_letter_is_kept_with_lower_score():
    results = find(NieRecognizer(), "NIE: X1234567A")

    assert len(results) == 1
    text, score = results[0]
    assert text == "X1234567A"
    assert 0 < score < 1.0


def test_nie_with_hyphens_and_valid_letter_gets_max_score():
    assert find(NieRecognizer(), "NIE: X-1234567-L.") == [("X-1234567-L", 1.0)]


def test_nie_with_hyphens_and_invalid_letter_is_kept_with_lower_score():
    results = find(NieRecognizer(), "NIE: X-1234567-A.")

    assert len(results) == 1
    text, score = results[0]
    assert text == "X-1234567-A"
    assert 0 < score < 1.0


def test_historia_clinica_without_context_keeps_base_score():
    assert find(HistoriaClinicaRecognizer(), "Número 7300451 en el informe") == [
        ("7300451", HISTORIA_CLINICA_BASE_SCORE)
    ]


@pytest.mark.parametrize(
    "text",
    [
        "DNI: 12345678Z",
        "DNI: 12345678-Z",
        "DNI: 12345678 Z",
        "DNI: 12.345.678-Z",
        "Petición PET-2026-000123",
        "Colegiado 99/00123",
        "CA 19-9 de 1.240 U/mL",
        "Fecha 14/03/1958",
        "Valor 12345,6",
    ],
)
def test_historia_clinica_ignores_parts_of_other_identifiers(text):
    assert find(HistoriaClinicaRecognizer(), text) == []


@pytest.mark.parametrize(
    "text",
    [
        "NHC 7300451 y DNI",
        "NHC: 7300451 F.NAC: 01/01/1950",
        "NHC 7300451 H",
        "NHC: 7300451-A",
    ],
)
def test_historia_clinica_followed_by_a_word_or_letter_is_still_found(text):
    assert find(HistoriaClinicaRecognizer(), text) == [
        ("7300451", HISTORIA_CLINICA_BASE_SCORE)
    ]


def test_name_after_solicitante_stops_before_next_label():
    text = "Solicitante : INÉS CARRASCAL OCHOA SERVICIO : ONCOLOGÍA MÉDICA"

    assert find_typed(solicitante_recognizer(), text) == [
        ("INÉS CARRASCAL OCHOA", "PERSONAL_SANITARIO", LABELED_ENTITY_SCORE)
    ]


@pytest.mark.parametrize(
    "text, name",
    [
        ("Paciente: ROSARIO ALBENDEA QUINTANAR", "ROSARIO ALBENDEA QUINTANAR"),
        ("Paciente: Rosario Albendea Quintanar. DNI: 12345678Z.", "Rosario Albendea Quintanar"),
        ("Paciente: Rosario Albendea Quintanar Edad: 68", "Rosario Albendea Quintanar"),
    ],
)
def test_name_after_paciente_is_found_without_label(text, name):
    assert find_typed(paciente_recognizer(), text) == [
        (name, "PACIENTE", LABELED_ENTITY_SCORE)
    ]


def test_name_after_label_does_not_include_title():
    text = "Médico solicitante: Dra. Inés Carrascal Ochoa"

    assert find(solicitante_recognizer(), text) == [
        ("Inés Carrascal Ochoa", LABELED_ENTITY_SCORE)
    ]


def test_name_after_label_stays_on_the_same_line():
    assert find(paciente_recognizer(), "Paciente:\nRosario Albendea Quintanar") == []


def test_surnames_first_name_header_does_not_include_next_labels():
    text = "ALBENDEA QUINTANAR, ROSARIO\nCaso: 99/00123\nEntidad: Hospital Universitario Monteluz"

    assert find_typed(ApellidosNombreRecognizer(), text) == [
        ("ALBENDEA QUINTANAR, ROSARIO", "PERSON", SURNAMES_FIRST_BASE_SCORE)
    ]


@pytest.mark.parametrize(
    "label",
    [
        "Paciente:",
        "Médico solicitante :",
        "Nombre:",
        "Apellidos y nombre:",
        "Nombre y apellidos:",
    ],
)
def test_surnames_first_name_after_name_label_gets_labeled_score(label):
    text = f"{label} ALBENDEA QUINTANAR, ROSARIO"

    # Las etiquetas solo afectan a la puntuación; el rol lo asigna detection.py.
    assert find_typed(ApellidosNombreRecognizer(), text) == [
        ("ALBENDEA QUINTANAR, ROSARIO", "PERSON", LABELED_ENTITY_SCORE)
    ]


def test_surnames_first_name_after_other_label_keeps_base_score():
    assert find(ApellidosNombreRecognizer(), "Diagnóstico: PÁNCREAS, CABEZA") == [
        ("PÁNCREAS, CABEZA", SURNAMES_FIRST_BASE_SCORE)
    ]


def test_surnames_first_name_label_must_be_on_the_same_line():
    text = "Paciente:\nALBENDEA QUINTANAR, ROSARIO"

    assert find(ApellidosNombreRecognizer(), text) == [
        ("ALBENDEA QUINTANAR, ROSARIO", SURNAMES_FIRST_BASE_SCORE)
    ]


def test_diagnosis_line_after_sentence_with_paciente_stays_below_finding_threshold():
    # Con 0,85 o con el refuerzo por contexto de Presidio superaría el umbral y
    # se borraría el diagnóstico.
    text = (
        "Se revisa la biopsia de la paciente en el comité de tumores digestivos.\n"
        "CARCINOMA DUCTAL, MODERADAMENTE DIFERENCIADO"
    )

    assert [score for _, score in find(ApellidosNombreRecognizer(), text)] == [
        SURNAMES_FIRST_BASE_SCORE
    ]
    assert SURNAMES_FIRST_BASE_SCORE < FINDING_THRESHOLD
    assert not ApellidosNombreRecognizer().context


@pytest.mark.parametrize(
    "text",
    [
        "Se comenta con ALBENDEA QUINTANAR, ROSARIO",
        "albendea quintanar, rosario",
    ],
)
def test_surnames_first_name_needs_line_start_and_uppercase(text):
    assert find(ApellidosNombreRecognizer(), text) == []


def test_surnames_first_name_base_score_is_below_labeled_names():
    # Una línea clínica en mayúsculas tiene la misma forma que «APELLIDOS, Nombre».
    assert SURNAMES_FIRST_BASE_SCORE < LABELED_ENTITY_SCORE
    assert find(ApellidosNombreRecognizer(), "CARCINOMA DUCTAL, MODERADAMENTE DIFERENCIADO") == [
        ("CARCINOMA DUCTAL, MODERADAMENTE DIFERENCIADO", SURNAMES_FIRST_BASE_SCORE)
    ]


ADDRESS = "Calle del Almendro Florido, 14, 3.º B, Villaserena (Valladolid)"


@pytest.mark.parametrize("label", ["Domicilio:", "Domicilio :"])
def test_address_after_label_runs_to_end_of_line(label):
    text = f"{label} {ADDRESS}\nTeléfono: 600 123 456"

    assert find_typed(DomicilioRecognizer(), text) == [
        (ADDRESS, "CALLE", LABELED_ENTITY_SCORE)
    ]


def test_address_stops_before_next_label():
    text = "Domicilio: Calle del Almendro Florido, 14, Teléfono: 600 123 456"

    assert find(DomicilioRecognizer(), text) == [
        ("Calle del Almendro Florido, 14", LABELED_ENTITY_SCORE)
    ]


@pytest.mark.parametrize(
    "label", ["CP:", "C.P.:", "Código postal:", "CÓDIGO POSTAL:", "Localidad:", "Municipio:", "Provincia:"]
)
def test_address_does_not_stop_before_address_labels(label):
    address = f"Calle del Almendro Florido, 14 {label} Villaserena"

    assert find(DomicilioRecognizer(), f"Domicilio: {address}") == [
        (address, LABELED_ENTITY_SCORE)
    ]


def test_dated_signature_name_excludes_date_and_time():
    text = "(12/09/2026 13:45 - ANDRÉS LOZOYA BENÍTEZ)"

    assert find_typed(FirmaFechadaRecognizer(), text) == [
        ("ANDRÉS LOZOYA BENÍTEZ", "PERSONAL_SANITARIO", LABELED_ENTITY_SCORE)
    ]


def test_dated_signature_needs_closing_parenthesis():
    assert find(FirmaFechadaRecognizer(), "(12/09/2026 13:45 - ANDRÉS LOZOYA BENÍTEZ") == []
