"""Confianza del documento para la anonimización (ACO-023).

La confianza mide si los datos personales de las categorías garantizadas se
han detectado bien. La duda de rol no la rebaja: para las personas se suman
las probabilidades de las cuatro etiquetas del modelo, no solo la ganadora.
"""

import logging

import numpy as np

from .analyzer import get_token_pipeline
from .detection import PERSON_TYPES
from .policy import Finding, is_guaranteed

logger = logging.getLogger("app.services.anonymization")

# Etiquetas del modelo que representan personas (ACO-022, P4).
PERSON_MODEL_LABELS = frozenset(
    {
        "NOMBRE_SUJETO_ASISTENCIA",
        "NOMBRE_PERSONAL_SANITARIO",
        "FAMILIARES_SUJETO_ASISTENCIA",
        "OTROS_SUJETO_ASISTENCIA",
    }
)


def _person_label_ids(pipe) -> set[int]:
    id2label = pipe.model.config.id2label
    return {
        int(index)
        for index, label in id2label.items()
        if label.split("-", 1)[-1] in PERSON_MODEL_LABELS
    }


def _token_person_probabilities(text: str, analyzer) -> list[tuple[int, int, float]]:
    """Probabilidad de persona por token, sumando las cuatro etiquetas.

    Devuelve una lista de (inicio, fin, probabilidad). Lanza si el pipeline no
    permite obtener las probabilidades; el llamador cae a la puntuación del
    hallazgo.
    """
    pipe = get_token_pipeline(analyzer)
    encoding = pipe.tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        return_offsets_mapping=True,
        return_special_tokens_mask=True,
    )
    offsets = encoding.pop("offset_mapping")[0].tolist()
    special_tokens = encoding.pop("special_tokens_mask")[0].tolist()
    encoding.pop("overflow_to_sample_mapping", None)

    # _forward necesita estos campos, igual que en el pipeline de Presidio.
    encoding["sentence"] = text
    encoding["is_last"] = True
    encoding["offset_mapping"] = offsets
    encoding["special_tokens_mask"] = special_tokens

    outputs = pipe.forward(encoding)
    logits = outputs["logits"][0].detach().cpu().numpy()
    shifted = np.exp(logits - logits.max(axis=-1, keepdims=True))
    probabilities = shifted / shifted.sum(axis=-1, keepdims=True)
    person_ids = _person_label_ids(pipe)

    tokens: list[tuple[int, int, float]] = []
    for index, (start, end) in enumerate(offsets):
        if special_tokens[index] or start == end:
            continue
        probability = float(
            sum(probabilities[index][label_id] for label_id in person_ids)
        )
        tokens.append((start, end, probability))
    return tokens


def _person_support(
    finding: Finding, tokens: list[tuple[int, int, float]]
) -> float:
    overlapping = [
        probability
        for start, end, probability in tokens
        if start < finding.end and end > finding.start
    ]
    if not overlapping:
        return finding.score
    return sum(overlapping) / len(overlapping)


def _category(finding: Finding) -> str:
    """Categoría de confianza: las cuatro etiquetas de persona son una sola."""
    if finding.entity_type in PERSON_TYPES:
        return "PERSON"
    return finding.entity_type


def document_confidence(text: str, findings: list[Finding], analyzer) -> float:
    """Mínimo del mejor soporte de cada categoría garantizada; 1,0 sin ninguna.

    Se agrupa por categoría para que el troceado de un mismo dato en varios
    hallazgos (por ejemplo, una tarjeta sanitaria partida en dos teléfonos) no
    rebaje la confianza si alguna de las partes se detectó con seguridad. Las
    cuatro etiquetas de persona cuentan como una sola categoría (ADR-013).
    """
    guaranteed = [finding for finding in findings if is_guaranteed(finding)]
    if not guaranteed:
        return 1.0

    tokens: list[tuple[int, int, float]] | None = None
    if any(finding.entity_type in PERSON_TYPES for finding in guaranteed):
        try:
            tokens = _token_person_probabilities(text, analyzer)
        except Exception:
            # Modo degradado: no se filtra contenido en el aviso.
            logger.warning(
                "Confianza del documento: no se pudieron obtener las "
                "probabilidades por etiqueta; se usa la puntuación del hallazgo"
            )
            tokens = None

    best_by_category: dict[str, float] = {}
    for finding in guaranteed:
        is_person = finding.entity_type in PERSON_TYPES
        if is_person and tokens is not None:
            support = _person_support(finding, tokens)
        else:
            support = finding.score
        category = _category(finding)
        best_by_category[category] = max(
            best_by_category.get(category, 0.0), support
        )

    return min(best_by_category.values())
