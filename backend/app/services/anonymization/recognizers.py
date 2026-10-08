"""Reconocedores propios de identificadores clínicos españoles (ACO-022)."""

import re

from presidio_analyzer import Pattern, PatternRecognizer

CONTROL_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
NIE_PREFIXES = {"X": "0", "Y": "1", "Z": "2"}

# Puntuaciones iniciales (ficha ACO-022, P6). La calibración corresponde a ACO-023.
ID_INVALID_LETTER_SCORE = 0.5
HISTORIA_CLINICA_BASE_SCORE = 0.3

DNI_CONTEXT = ["dni", "nif", "identidad"]
NIE_CONTEXT = ["nie", "dni", "nif", "identidad"]
# Palabras sueltas: «número de historia» o «historia clínica» se reconocen por
# «historia». No se incluyen «número» ni «clínica», que también acompañan a
# teléfonos y direcciones.
HISTORIA_CLINICA_CONTEXT = ["nhc", "historia", "h.c.", "hc"]


# Separador opcional antes de la letra: guion, o espacio solo con letra
# mayúscula para no tomar «12345678 y» por un DNI (ficha ACO-022, B3).
# Presidio busca sin distinguir mayúsculas; (?-i:...) lo anula en ese tramo.
_LETTER = r"(?:-?[A-Z]|(?-i: [A-Z]))(?!\w)"
DNI_REGEX = r"(?<![\w.-])(?:\d{8}|\d{2}\.\d{3}\.\d{3})" + _LETTER
NIE_REGEX = r"(?<![\w-])[XYZ]-?\d{7}" + _LETTER


def _has_valid_control_letter(digits: str, letter: str) -> bool:
    return CONTROL_LETTERS[int(digits) % 23] == letter.upper()


def _compact(pattern_text: str) -> str:
    """Quita los separadores: la letra se valida sobre los dígitos sin ellos."""
    return re.sub(r"[^0-9A-Za-z]", "", pattern_text)


class DniRecognizer(PatternRecognizer):
    """DNI: 8 dígitos y letra de control.

    Con letra válida la puntuación sube al máximo. Con letra no válida el
    hallazgo se conserva con la puntuación del patrón (ficha ACO-022, P5).
    """

    def __init__(self):
        super().__init__(
            supported_entity="ES_DNI",
            name="DniRecognizer",
            supported_language="es",
            patterns=[
                Pattern("dni", DNI_REGEX, ID_INVALID_LETTER_SCORE),
            ],
            context=DNI_CONTEXT,
        )

    def validate_result(self, pattern_text: str) -> bool | None:
        # None conserva la puntuación del patrón; False descartaría el hallazgo.
        dni = _compact(pattern_text)
        return True if _has_valid_control_letter(dni[:8], dni[8]) else None


class NieRecognizer(PatternRecognizer):
    """NIE: X, Y o Z, 7 dígitos y letra de control. Mismo criterio que el DNI."""

    def __init__(self):
        super().__init__(
            supported_entity="ES_NIE",
            name="NieRecognizer",
            supported_language="es",
            patterns=[
                Pattern("nie", NIE_REGEX, ID_INVALID_LETTER_SCORE),
            ],
            context=NIE_CONTEXT,
        )

    def validate_result(self, pattern_text: str) -> bool | None:
        nie = _compact(pattern_text)
        digits = NIE_PREFIXES[nie[0].upper()] + nie[1:8]
        return True if _has_valid_control_letter(digits, nie[8]) else None


class HistoriaClinicaRecognizer(PatternRecognizer):
    """Número de historia clínica: 5 a 9 cifras.

    La puntuación base queda por debajo del umbral de hallazgo inicial y solo
    lo supera con contexto (ficha ACO-022, P6).
    """

    def __init__(self):
        super().__init__(
            supported_entity="ES_HISTORIA_CLINICA",
            name="HistoriaClinicaRecognizer",
            supported_language="es",
            patterns=[
                Pattern(
                    "historia_clinica",
                    # No toma los dígitos de un DNI con la letra separada («12345678-Z»).
                    r"(?<![\w.,/-])\d{5,9}(?!\w)(?![.,/-]\d)(?!" + _LETTER + ")",
                    HISTORIA_CLINICA_BASE_SCORE,
                ),
            ],
            context=HISTORIA_CLINICA_CONTEXT,
        )


def build_recognizers() -> list[PatternRecognizer]:
    return [DniRecognizer(), NieRecognizer(), HistoriaClinicaRecognizer()]
