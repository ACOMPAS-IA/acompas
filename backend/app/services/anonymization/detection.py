"""Detección de entidades para la anonimización (ACO-022).

Devuelve todo lo que detecta el motor, sin filtrar por puntuación ni por tipo.
Qué se anonimiza y con qué umbral lo decide ACO-023.
"""

from dataclasses import dataclass

from presidio_analyzer import AnalyzerEngine

from .analyzer import DEFAULT_ENTITIES


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int
    score: float
    # Rol de la persona detectada. Vacío hasta que se asigne el rol (ficha ACO-022, B1).
    role: str | None = None


def detect_entities(text: str, analyzer: AnalyzerEngine) -> list[Detection]:
    """Analiza `text` y devuelve todas las detecciones, ordenadas por posición."""
    results = analyzer.analyze(text=text, language="es", entities=DEFAULT_ENTITIES)

    return sorted(
        (
            Detection(
                entity_type=result.entity_type,
                start=result.start,
                end=result.end,
                score=result.score,
            )
            for result in results
        ),
        key=lambda detection: (detection.start, detection.end),
    )
