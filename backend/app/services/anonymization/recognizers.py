"""Reconocedores propios de identificadores clínicos españoles (ACO-022)."""

import re

from presidio_analyzer import Pattern, PatternRecognizer

CONTROL_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
NIE_PREFIXES = {"X": "0", "Y": "1", "Z": "2"}

# Puntuaciones iniciales (ficha ACO-022, P6). La calibración corresponde a ACO-023.
ID_INVALID_LETTER_SCORE = 0.5
HISTORIA_CLINICA_BASE_SCORE = 0.3
LABELED_ENTITY_SCORE = 0.85
SURNAMES_FIRST_BASE_SCORE = 0.3

DNI_CONTEXT = ["dni", "nif", "identidad"]
NIE_CONTEXT = ["nie", "dni", "nif", "identidad"]
# Palabras sueltas: «número de historia» o «historia clínica» se reconocen por
# «historia». No se incluyen «número» ni «clínica», que también acompañan a
# teléfonos y direcciones.
HISTORIA_CLINICA_CONTEXT = ["nhc", "historia", "h.c.", "hc"]
# Etiquetas de nombre: tras ellas, «APELLIDOS, Nombre» es un nombre con
# etiqueta. Solo afectan a la puntuación de R-05, no al rol (ficha ACO-022, P6).
NAME_LABELS = [
    "Paciente",
    "Solicitante",
    "Nombre",
    "Apellidos y nombre",
    "Nombre y apellidos",
]

# Inicio de una firma fechada, «(dd/mm/aaaa hh:mm - », antes del nombre.
SIGNATURE_PREFIX = r"\(\d{2}/\d{2}/\d{4} \d{2}:\d{2} - "


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
                    # Con 8 cifras y letra suelta detrás es un DNI con la letra
                    # separada («12345678-Z»): no se toma. Con otra longitud se
                    # detecta aunque le siga una letra («7300451 F.NAC»).
                    r"(?<![\w.,/-])(?:\d{8}(?!" + _LETTER + r")|\d{5,7}|\d{9})"
                    r"(?!\w)(?![.,/-]\d)",
                    HISTORIA_CLINICA_BASE_SCORE,
                ),
            ],
            context=HISTORIA_CLINICA_CONTEXT,
        )


_UPPER = "A-ZÁÉÍÓÚÜÑ"
_LOWER = "a-záéíóúüñ"
# Palabra en mayúsculas («ALBENDEA», «LOZOYA-BENÍTEZ»).
_UPPER_WORD = rf"[{_UPPER}]+(?:-[{_UPPER}]+)*"
# Palabra de nombre con inicial mayúscula («Rosario», «ROSARIO»).
_NAME_WORD = rf"[{_UPPER}][{_UPPER}{_LOWER}]*(?:-[{_UPPER}][{_UPPER}{_LOWER}]*)*"
# Etiqueta de campo: palabra con inicial mayúscula seguida de «:», con o sin
# espacio («SERVICIO :», «Edad:»). Los nombres y direcciones se detienen antes.
_FIELD_LABEL = rf"(?-i:[{_UPPER}][\w.]*) ?:"
# Palabra de nombre que no es el inicio de la siguiente etiqueta.
_NAME_WORD_NOT_LABEL = rf"(?!{_FIELD_LABEL})(?-i:{_NAME_WORD})(?![\w-])"
# Etiquetas que forman parte de la dirección: R-06 no se detiene ante ellas (ficha ACO-022, B8).
_ADDRESS_LABELS = r"(?:CP|C\.P\.|Código postal|postal|Localidad|Municipio|Provincia) ?:"


def _labeled_name_regex(label: str, words: int) -> str:
    """1 a `words` palabras de nombre tras «label:», sin la etiqueta.

    Un tratamiento justo después de la etiqueta («Solicitante: Dra. Inés…») no
    forma parte del nombre.
    """
    return (
        rf"(?<=\b{label} ?:[ \t]*(?:Dra?\.[ \t]*)?)(?!Dra?\.)"
        rf"{_NAME_WORD_NOT_LABEL}(?: {_NAME_WORD_NOT_LABEL}){{0,{words - 1}}}"
    )


class NombreTrasEtiquetaRecognizer(PatternRecognizer):
    """R-04: nombre tras una etiqueta que indica el rol («Paciente:», «Solicitante:»).

    El separador entre palabras es un espacio literal: el nombre no pasa de línea.
    """

    def __init__(self, label: str, entity: str, name: str):
        super().__init__(
            supported_entity=entity,
            name=name,
            supported_language="es",
            patterns=[Pattern(name, _labeled_name_regex(label, 5), LABELED_ENTITY_SCORE)],
        )


class ApellidosNombreRecognizer(PatternRecognizer):
    """R-05: «APELLIDOS, Nombre» al principio de línea o tras una etiqueta.

    Una línea clínica en mayúsculas tiene la misma forma («CARCINOMA DUCTAL,
    MODERADAMENTE DIFERENCIADO»). Solo justo detrás de una etiqueta de nombre
    en la misma línea tiene la puntuación de un nombre con etiqueta; en los
    demás casos queda por debajo del umbral de hallazgo inicial. No usa palabras
    de contexto: Presidio las busca también en la frase anterior (ficha ACO-022, P6).
    """

    def __init__(self):
        name_label = rf"\b(?:{'|'.join(NAME_LABELS)}) ?:[ \t]*"
        body = (
            rf"(?-i:{_UPPER_WORD}(?: {_UPPER_WORD}){{0,2}}), "
            rf"{_NAME_WORD_NOT_LABEL}(?: {_NAME_WORD_NOT_LABEL}){{0,3}}"
        )
        super().__init__(
            supported_entity="PERSON",
            name="ApellidosNombreRecognizer",
            supported_language="es",
            patterns=[
                Pattern(
                    "apellidos_nombre_etiqueta",
                    rf"(?<={name_label}){body}",
                    LABELED_ENTITY_SCORE,
                ),
                Pattern(
                    "apellidos_nombre",
                    rf"(?<=^[ \t]*|\w ?:[ \t]*)(?<!{name_label}){body}",
                    SURNAMES_FIRST_BASE_SCORE,
                ),
            ],
        )


class DomicilioRecognizer(PatternRecognizer):
    """R-06: dirección tras «Domicilio:» hasta el final de la línea.

    Codicioso a propósito, porque piso y puerta no tienen formato cerrado. Se
    detiene antes de la siguiente etiqueta salvo que sea parte de la dirección
    («CP:», «Localidad:»…) (ficha ACO-022, B8).
    """

    def __init__(self):
        super().__init__(
            supported_entity="CALLE",
            name="DomicilioRecognizer",
            supported_language="es",
            patterns=[
                Pattern(
                    "domicilio",
                    # Lo más corto que acabe en fin de línea o antes de una etiqueta.
                    r"(?<=\bDomicilio ?:[ \t]*)[^\s,;](?:[^\r\n]*?[^\s,;])?"
                    rf"(?=[ \t,;]*(?:\r?$|[ \t](?!{_ADDRESS_LABELS}){_FIELD_LABEL}))",
                    LABELED_ENTITY_SCORE,
                ),
            ],
        )


class FirmaFechadaRecognizer(PatternRecognizer):
    """R-07: nombre en mayúsculas en una firma «(dd/mm/aaaa hh:mm - NOMBRE)».

    Sin paréntesis de cierre no hay hallazgo. La fecha y la hora no forman parte de él.
    """

    def __init__(self):
        super().__init__(
            supported_entity="PERSONAL_SANITARIO",
            name="FirmaFechadaRecognizer",
            supported_language="es",
            patterns=[
                Pattern(
                    "firma_fechada",
                    rf"(?<={SIGNATURE_PREFIX})(?-i:{_UPPER_WORD}(?: {_UPPER_WORD}){{0,4}})(?=\))",
                    LABELED_ENTITY_SCORE,
                ),
            ],
        )


def build_recognizers() -> list[PatternRecognizer]:
    return [
        DniRecognizer(),
        NieRecognizer(),
        HistoriaClinicaRecognizer(),
        NombreTrasEtiquetaRecognizer("Paciente", "PACIENTE", "NombreTrasPacienteRecognizer"),
        NombreTrasEtiquetaRecognizer(
            "Solicitante", "PERSONAL_SANITARIO", "NombreTrasSolicitanteRecognizer"
        ),
        ApellidosNombreRecognizer(),
        DomicilioRecognizer(),
        FirmaFechadaRecognizer(),
    ]
