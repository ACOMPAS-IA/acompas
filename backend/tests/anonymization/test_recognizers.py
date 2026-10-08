import pytest

from app.services.anonymization.recognizers import (
    HISTORIA_CLINICA_BASE_SCORE,
    DniRecognizer,
    HistoriaClinicaRecognizer,
    NieRecognizer,
)

# Sin modelo ni red: se usa cada reconocedor aislado, sin refuerzo por contexto.


def find(recognizer, text):
    return [
        (text[result.start : result.end], result.score)
        for result in recognizer.analyze(
            text=text, entities=recognizer.supported_entities, nlp_artifacts=None
        )
    ]


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


def test_historia_clinica_followed_by_a_word_is_still_found():
    assert find(HistoriaClinicaRecognizer(), "NHC 7300451 y DNI") == [
        ("7300451", HISTORIA_CLINICA_BASE_SCORE)
    ]
