"""Política de anonimización y filtros de falsos positivos (ACO-023).

Separa lo que el motor detecta de lo que finalmente se anonimiza. No modifica
las detecciones originales y no necesita el modelo: los tests de política
pueden construirlas a mano.
"""

import re
import unicodedata
from dataclasses import dataclass

from .analyzer import DEFAULT_ENTITIES
from .config import AnonymizationSettings
from .detection import Detection

PERSON_TYPES = ("PACIENTE", "PERSONAL_SANITARIO", "FAMILIAR", "PERSON")

# Etiquetas de persona de ACO-022 (B4).
PERSON_LABELS = {
    "PACIENTE": "[PACIENTE]",
    "PERSONAL_SANITARIO": "[SANITARIO_n]",
    "FAMILIAR": "[FAMILIAR_n]",
    "PERSON": "[PERSONA_n]",
}


@dataclass(frozen=True)
class EntityPolicy:
    anonymize: bool
    guaranteed: bool
    label: str | None


# Clasificación de todos los tipos de DEFAULT_ENTITIES. Un tipo nuevo sin
# clasificar detiene el proceso: no se adivina su política.
POLICY: dict[str, EntityPolicy] = {
    # Personas: siempre, con rol (ADR-013).
    **{
        entity_type: EntityPolicy(True, True, label)
        for entity_type, label in PERSON_LABELS.items()
    },
    # Identificadores garantizados (ADR-013).
    "ES_DNI": EntityPolicy(True, True, "[DNI]"),
    "ES_NIE": EntityPolicy(True, True, "[NIE]"),
    "ES_HISTORIA_CLINICA": EntityPolicy(True, True, "[NHC]"),
    "ID_ASEGURAMIENTO": EntityPolicy(True, True, "[ID_ASEGURAMIENTO]"),
    "ID_CONTACTO_ASISTENCIAL": EntityPolicy(True, True, "[ID_CONTACTO]"),
    "ID_EMPLEO_PERSONAL_SANITARIO": EntityPolicy(True, True, "[ID_EMPLEO]"),
    "ID_TITULACION_PERSONAL_SANITARIO": EntityPolicy(True, True, "[ID_TITULACION]"),
    # Contacto y dirección (ADR-013).
    "PHONE_NUMBER": EntityPolicy(True, True, "[TELEFONO]"),
    "EMAIL_ADDRESS": EntityPolicy(True, True, "[EMAIL]"),
    "CALLE": EntityPolicy(True, True, "[DIRECCION]"),
    # La fecha de nacimiento se decide por contexto en select_findings().
    "DATE_TIME": EntityPolicy(False, False, None),
    # Categorías sin garantía: se sustituyen si se detectan (ADR-013).
    "HOSPITAL": EntityPolicy(True, False, "[HOSPITAL]"),
    "CENTRO_SALUD": EntityPolicy(True, False, "[CENTRO_SALUD]"),
    "INSTITUCION": EntityPolicy(True, False, "[INSTITUCION]"),
    # La localidad es garantizada, pero la etiqueta mezcla localidad y
    # provincia; se anonimiza y no cuenta para la confianza (ficha, P5).
    "TERRITORIO": EntityPolicy(True, False, "[TERRITORIO]"),
    # Contexto clínico que no se anonimiza (ADR-013).
    "AGE": EntityPolicy(False, False, None),
    "SEXO": EntityPolicy(False, False, None),
    "PROFESION": EntityPolicy(False, False, None),
    "PAIS": EntityPolicy(False, False, None),
}

# Términos clínicos que el modelo puede confundir con datos personales. Solo
# descartan un hallazgo cuando todo su fragmento es el término (ficha, P7).
ALLOW_LIST = frozenset(
    {
        "CA 19-9",
        "CEA",
        "CK7",
        "CK19",
        "CK20",
        "CDX2",
        "Ki-67",
        "PD-L1",
        "HER2",
        "MSI",
        "MMR",
        "BRCA1",
        "BRCA2",
        "KRAS",
        "EGFR",
        "ALK",
        "ROS1",
        "BRAF",
        "PIK3CA",
        "CARCINOMA DUCTAL",
        "ADENOCARCINOMA",
        "MODERADAMENTE DIFERENCIADO",
        "CARCINOMA DUCTAL MODERADAMENTE DIFERENCIADO",
        "mFOLFIRINOX",
        "FOLFOX",
        "FOLFIRI",
        "ECOG",
        "PAAF",
        "BAG",
        "CPRE",
        "AJCC",
        "TC",
        "PET",
        "RM",
        "TAC",
    }
)

# Tratamientos que pueden aparecer solos como fragmento detectado. No forman
# parte de un nombre utilizable: si se conservaran, la etiqueta de persona
# quedaría sin número o duplicada junto al dato real (ficha, P7 y P12).
TREATMENT_LABELS = frozenset({"sr", "sra", "d", "dna"})

# Etiquetas de rol que el modelo puede detectar como si fueran el valor. Solo
# se descarta el hallazgo cuando todo su fragmento es la etiqueta (ficha, P7).
# Incluye las mismas pistas que usa ACO-022 para asignar el rol.
ROLE_LABELS = frozenset(
    {
        "paciente",
        "solicitante",
        "medico solicitante",
        "medico peticionario",
        "fdo",
        "validado por",
        "dr",
        "dra",
        "doctor",
        "doctora",
        "marido",
        "esposa",
        "pareja",
        "hijo",
        "hija",
        "madre",
        "padre",
        "hermano",
        "hermana",
        "tutor",
        "tutora",
    }
)

# Pistas de fecha de nacimiento (ficha, 8.4). La pista tiene que ir
# inmediatamente antes de la fecha: solo espacios y, como mucho, dos puntos.
_BIRTH_CUES = re.compile(
    r"(?:fecha de nacimiento|fecha nac\.?|f\.?\s*nac\.?|nacimiento|nacido el|nacida el|dob)"
    r"\s*:?\s*\Z",
    re.IGNORECASE,
)
_BIRTH_WINDOW = 40


class UnclassifiedEntityError(ValueError):
    """Un tipo de entidad detectado no tiene política de anonimización."""


@dataclass(frozen=True)
class Finding:
    """Hallazgo que pasa la política y se va a anonimizar."""

    entity_type: str
    start: int
    end: int
    score: float


def _normalize_term(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_marks = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return " ".join(re.sub(r"[^0-9a-z]+", " ", without_marks.casefold()).split())


_NORMALIZED_ALLOW_LIST = frozenset(_normalize_term(term) for term in ALLOW_LIST)
_NORMALIZED_ROLE_LABELS = frozenset(
    _normalize_term(label) for label in ROLE_LABELS
)
_NORMALIZED_TREATMENT_LABELS = frozenset(
    _normalize_term(label) for label in TREATMENT_LABELS
)


def is_allowlisted(fragment: str) -> bool:
    return _normalize_term(fragment) in _NORMALIZED_ALLOW_LIST


def is_punctuation(fragment: str) -> bool:
    """Solo puntuación o espacios: nunca es un dato personal."""
    return not any(char.isalnum() for char in fragment)


def is_role_label(fragment: str) -> bool:
    """El fragmento entero es una etiqueta de rol, no el valor que la sigue."""
    return _normalize_term(fragment) in _NORMALIZED_ROLE_LABELS


def is_treatment(fragment: str) -> bool:
    """El fragmento entero es un tratamiento suelto, sin nombre que lo siga."""
    return _normalize_term(fragment) in _NORMALIZED_TREATMENT_LABELS


def is_noise(fragment: str) -> bool:
    """Fragmentos que el modelo detecta pero no son datos personales."""
    return (
        is_punctuation(fragment)
        or is_role_label(fragment)
        or is_treatment(fragment)
    )


def is_birth_date(text: str, detection: Detection | Finding) -> bool:
    before = text[max(0, detection.start - _BIRTH_WINDOW) : detection.start]
    return bool(_BIRTH_CUES.search(before))


def is_guaranteed(finding: Finding) -> bool:
    # Los DATE_TIME que llegan aquí han pasado el filtro de nacimiento.
    if finding.entity_type == "DATE_TIME":
        return True
    return POLICY[finding.entity_type].guaranteed


def label_for(finding: Finding) -> str:
    if finding.entity_type == "DATE_TIME":
        return "[FECHA_NACIMIENTO]"
    label = POLICY[finding.entity_type].label
    if label is None:
        raise UnclassifiedEntityError(f"sin etiqueta para {finding.entity_type}")
    return label


def _priority(finding: Finding) -> tuple[bool, float, int, int]:
    # Garantizada > puntuación > fragmento más largo > posición más temprana.
    return (
        is_guaranteed(finding),
        finding.score,
        finding.end - finding.start,
        -finding.start,
    )


def _merge_overlaps(text: str, findings: list[Finding]) -> list[Finding]:
    merged: list[Finding] = []
    for finding in sorted(findings, key=lambda item: (item.start, item.end)):
        if merged and finding.start < merged[-1].end:
            previous = merged[-1]
            winner = previous if _priority(previous) >= _priority(finding) else finding
            # Si un hallazgo contiene al otro y lo que sobra es solo
            # puntuación o espacios, se conserva el fragmento del ganador (por
            # ejemplo, el DNI sin el punto que arrastraba el número de
            # historia). Si sobra texto, se une para no dejar nada sin cubrir.
            nested = (
                previous.start <= finding.start and finding.end <= previous.end
            ) or (
                finding.start <= previous.start and previous.end <= finding.end
            )
            if nested:
                inner, outer = (
                    (finding, previous)
                    if previous.start <= finding.start
                    and finding.end <= previous.end
                    else (previous, finding)
                )
                extra = (
                    text[outer.start : inner.start] + text[inner.end : outer.end]
                )
                if any(char.isalnum() for char in extra):
                    start, end = outer.start, outer.end
                else:
                    start, end = inner.start, inner.end
            else:
                start, end = min(previous.start, finding.start), max(
                    previous.end, finding.end
                )
            merged[-1] = Finding(
                entity_type=winner.entity_type,
                start=start,
                end=end,
                score=winner.score,
            )
        else:
            merged.append(finding)
    return merged


def _trim_span(text: str, start: int, end: int) -> tuple[int, int] | None:
    """Quita espacios de los extremos para no arrastrar saltos de línea."""
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if start == end:
        return None
    return start, end


_ADJACENT_GAP = re.compile(r"\s*,?\s*\Z")


def _merge_adjacent_people(text: str, findings: list[Finding]) -> list[Finding]:
    """Une un nombre partido por la coma de «APELLIDOS, NOMBRE».

    Solo se unen dos hallazgos de persona consecutivos cuando entre ellos no
    hay nada más que espacios y, como mucho, una coma, y el primero acaba en
    coma. Sin esta unión, la cabecera «ALBENDEA QUINTANAR, ROSARIO» se
    etiquetaría como dos pacientes distintos.
    """
    merged: list[Finding] = []
    for finding in findings:
        previous = merged[-1] if merged else None
        if (
            previous is not None
            and previous.entity_type in PERSON_TYPES
            and finding.entity_type in PERSON_TYPES
            and text[previous.end - 1 : previous.end] == ","
            and _ADJACENT_GAP.fullmatch(text[previous.end : finding.start])
        ):
            merged[-1] = Finding(
                entity_type=(
                    previous.entity_type
                    if previous.entity_type == finding.entity_type
                    else "PERSON"
                ),
                start=previous.start,
                end=finding.end,
                score=max(previous.score, finding.score),
            )
        else:
            merged.append(finding)
    return merged


def select_findings(
    text: str,
    detections: list[Detection],
    settings: AnonymizationSettings,
) -> list[Finding]:
    """Aplica umbral, política, ruido, allow-list, nacimiento y solapes."""
    selected: list[Finding] = []
    for detection in detections:
        if detection.score < settings.finding_threshold:
            continue

        policy = POLICY.get(detection.entity_type)
        if policy is None:
            raise UnclassifiedEntityError(
                f"tipo sin política: {detection.entity_type}"
            )

        span = _trim_span(text, detection.start, detection.end)
        if span is None:
            continue
        start, end = span
        fragment = text[start:end]
        if is_noise(fragment):
            continue

        finding = Finding(
            entity_type=detection.entity_type,
            start=start,
            end=end,
            score=detection.score,
        )

        if not policy.anonymize:
            if detection.entity_type == "DATE_TIME" and is_birth_date(text, finding):
                selected.append(finding)
            continue

        if is_allowlisted(fragment):
            continue

        selected.append(finding)

    return _merge_adjacent_people(text, _merge_overlaps(text, selected))


def unclassified_entities() -> set[str]:
    """Tipos de DEFAULT_ENTITIES que no tienen política (debe estar vacío)."""
    return set(DEFAULT_ENTITIES) - set(POLICY)
