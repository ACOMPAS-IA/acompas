"""Detección de entidades para la anonimización (ACO-022).

Devuelve todo lo que detecta el motor, sin filtrar por puntuación ni por tipo.
Qué se anonimiza y con qué umbral lo decide ACO-023.
"""

import dataclasses
import re
import unicodedata
from dataclasses import dataclass

from presidio_analyzer import AnalyzerEngine

from .analyzer import DEFAULT_ENTITIES
from .recognizers import SIGNATURE_PREFIX

# Tipos de persona; PERSON es el genérico cuando el rol no está claro (ficha ACO-022, P4).
PERSON_TYPES = ("PACIENTE", "PERSONAL_SANITARIO", "FAMILIAR", "PERSON")

# Pistas de rol (ficha ACO-022, P7). Sin distinguir mayúsculas y con o sin
# espacio antes de los dos puntos (B7).
ROLE_CUES = {
    "PERSONAL_SANITARIO": [
        r"\bDra?\.",
        r"\bSolicitante ?:",
        r"\bMédico solicitante ?:",
        r"\bMédico peticionario ?:",
        r"\bFdo\. ?:",
        r"\bValidado por ?:",
        SIGNATURE_PREFIX,
    ],
    "PACIENTE": [r"\bPaciente ?:"],
}

# La pista tiene que ir inmediatamente antes del nombre: entre ambos solo
# puede haber espacios en blanco, incluido un salto de línea (B7).
_CUE_PATTERNS = {
    role: re.compile(rf"(?:{'|'.join(cues)})\s*\Z", re.IGNORECASE)
    for role, cues in ROLE_CUES.items()
}
# Lo que se mira antes de cada hallazgo: basta para la pista más larga.
_CUE_WINDOW = 40

# Un tratamiento de rol al principio del propio hallazgo también es pista (B9).
_LEADING_ROLE_TREATMENT = re.compile(r"\A\s*Dra?\.", re.IGNORECASE)

# Tratamientos que se ignoran al comparar nombres (B9). Sin tildes ni
# puntuación: «Dña.» llega aquí como «dna».
_TREATMENTS = frozenset({"dr", "dra", "sr", "sra", "d", "dna"})


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int
    score: float
    # Rol de la persona detectada: repite el tipo en los hallazgos de persona y
    # es None en los demás. Solo lo fija assign_roles (ficha ACO-022, B5).
    role: str | None = None


def _cue_role(text: str, start: int, end: int) -> str | None:
    before = text[max(0, start - _CUE_WINDOW) : start]
    for role, pattern in _CUE_PATTERNS.items():
        if pattern.search(before):
            return role
    if _LEADING_ROLE_TREATMENT.match(text[start:end]):
        return "PERSONAL_SANITARIO"
    return None


def _normalize_name(fragment: str) -> tuple[str, ...]:
    """Palabras del nombre para comparar menciones (ficha ACO-022, B9).

    Quita tildes, pasa a minúsculas, separa por puntuación e ignora los
    tratamientos iniciales. El orden no cuenta: se devuelven ordenadas.
    """
    decomposed = unicodedata.normalize("NFKD", fragment)
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    words = re.sub(r"[^0-9a-z]+", " ", without_marks.casefold()).split()
    while words and words[0] in _TREATMENTS:
        words.pop(0)
    return tuple(sorted(words))


def _people_with_name(
    index: int,
    name: tuple[str, ...],
    names: list[tuple[str, ...]],
    roles: list[str | None],
) -> dict[tuple[str, ...], set[str]]:
    """Personas distintas cuyas palabras contienen todas las de `name` (regla 8)."""
    found: dict[tuple[str, ...], set[str]] = {}
    for other_index, (other_name, other_role) in enumerate(zip(names, roles)):
        if other_index == index or not other_name:
            continue
        if set(name) <= set(other_name):
            found.setdefault(other_name, set()).add(other_role)
    return found


def _propagated_role(
    index: int,
    name: tuple[str, ...],
    names: list[tuple[str, ...]],
    roles: list[str | None],
    sources: list[int],
) -> str | None:
    """Rol que hereda una mención sin pista propia (ficha ACO-022, B9; ADR-014).

    Devuelve None si no hay nada que propagar y la mención conserva el tipo del
    modelo. `roles` es el rol de la primera fase (pista o modelo), para que el
    resultado no dependa del orden de los hallazgos.
    """
    if not name:
        return None

    # Una palabra suelta no hereda (regla 5), pero la ambigüedad de la regla 8
    # sigue dejándola como persona genérica.
    if len(name) < 2:
        found = _people_with_name(index, name, names, roles)
        found_roles = {role for roles_ in found.values() for role in roles_}
        if "PERSON" in found_roles or len(found_roles) > 1:
            return "PERSON"
        return None

    exact = [source for source in sources if names[source] == name]
    if exact:
        exact_roles = {roles[source] for source in exact}
        return exact_roles.pop() if len(exact_roles) == 1 else "PERSON"

    # Mención parcial: más corta que el nombre con pista y contenida en él.
    partial = [source for source in sources if set(name) < set(names[source])]
    if not partial:
        return None
    source_roles = {roles[source] for source in partial}
    if len(source_roles) > 1:
        return "PERSON"
    inherited = source_roles.pop()

    # «Otra persona»: nombre distinto y no contenido en el de la fuente (regla 4).
    source_names = [names[source] for source in partial]
    competitors = _people_with_name(index, name, names, roles)
    for other_name, other_roles in list(competitors.items()):
        if any(set(other_name) <= set(source_name) for source_name in source_names):
            del competitors[other_name]
    if any(
        role == "PERSON" or role != inherited
        for roles_ in competitors.values()
        for role in roles_
    ):
        return "PERSON"
    return inherited


def assign_roles(text: str, detections: list[Detection]) -> list[Detection]:
    """Asigna el rol de las personas por pistas y lo propaga (ficha ACO-022, P12).

    Primera fase: un hallazgo de persona con una pista inmediatamente antes toma
    su rol aunque el modelo diga otro. Segunda fase: las menciones sin pista
    heredan el rol de otra mención del mismo nombre, con las reglas de ADR-014.
    No cambia posiciones ni puntuaciones, ni elimina hallazgos.
    """
    is_person = [detection.entity_type in PERSON_TYPES for detection in detections]
    cues = [
        _cue_role(text, detection.start, detection.end) if person else None
        for detection, person in zip(detections, is_person)
    ]
    roles = [
        (cue or detection.entity_type) if person else None
        for detection, cue, person in zip(detections, cues, is_person)
    ]
    names = [
        _normalize_name(text[detection.start : detection.end]) if person else ()
        for detection, person in zip(detections, is_person)
    ]
    sources = [
        index for index, person in enumerate(is_person) if person and cues[index] and names[index]
    ]

    assigned = []
    for index, detection in enumerate(detections):
        if not is_person[index]:
            assigned.append(dataclasses.replace(detection, role=None))
            continue
        role = roles[index]
        if index not in sources:
            role = _propagated_role(index, names[index], names, roles, sources) or role
        assigned.append(dataclasses.replace(detection, entity_type=role, role=role))
    return assigned


def detect_entities(text: str, analyzer: AnalyzerEngine) -> list[Detection]:
    """Analiza `text` y devuelve todas las detecciones, ordenadas por posición."""
    results = analyzer.analyze(text=text, language="es", entities=DEFAULT_ENTITIES)

    detections = [
        Detection(
            entity_type=result.entity_type,
            start=result.start,
            end=result.end,
            score=result.score,
        )
        for result in results
    ]
    return sorted(
        assign_roles(text, detections),
        key=lambda detection: (detection.start, detection.end),
    )
