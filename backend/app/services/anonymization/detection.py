"""Detección de entidades para la anonimización (ACO-022).

Devuelve todo lo que detecta el motor, sin filtrar por puntuación ni por tipo.
Qué se anonimiza y con qué umbral lo decide ACO-023.
"""

import dataclasses
import re
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


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int
    score: float
    # Rol de la persona detectada: repite el tipo en los hallazgos de persona y
    # es None en los demás. Solo lo fija assign_roles (ficha ACO-022, B5).
    role: str | None = None


def _cue_role(text: str, start: int) -> str | None:
    before = text[max(0, start - _CUE_WINDOW) : start]
    for role, pattern in _CUE_PATTERNS.items():
        if pattern.search(before):
            return role
    return None


def assign_roles(text: str, detections: list[Detection]) -> list[Detection]:
    """Asigna el rol de las personas por las pistas de contexto (ficha ACO-022, P7).

    Si un hallazgo de persona tiene una pista inmediatamente antes, toma su rol
    aunque el modelo diga otro. Si no, conserva el tipo recibido. No cambia
    posiciones ni puntuaciones, ni elimina hallazgos.
    """
    assigned = []
    for detection in detections:
        entity_type = detection.entity_type
        if entity_type in PERSON_TYPES:
            entity_type = _cue_role(text, detection.start) or entity_type
        role = entity_type if entity_type in PERSON_TYPES else None
        assigned.append(dataclasses.replace(detection, entity_type=entity_type, role=role))
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
