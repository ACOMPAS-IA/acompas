"""Confianza del documento para la anonimización (ACO-023).

La confianza mide si los datos personales de las categorías garantizadas se
han detectado bien. Se calcula por dato, no por categoría: dos datos distintos
de la misma categoría cuentan por separado y el débil rebaja la confianza. La
duda de rol no la rebaja: para las personas se suman las probabilidades de las
cuatro etiquetas del modelo, no solo la ganadora.
"""

import logging

import numpy as np

from .analyzer import get_token_pipeline
from .detection import PERSON_TYPES
from .policy import Finding, is_guaranteed
from .replacement import group_person_findings

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

# Ventanas del tokenizador. El modelo MEDDOCAN admite 512 tokens; los
# documentos pueden ser más largos y las personas del final no pueden caer a
# la puntuación del hallazgo por el truncado.
WINDOW_MAX_LENGTH = 512
WINDOW_STRIDE = 64


def _person_label_ids(pipe) -> set[int]:
    id2label = pipe.model.config.id2label
    return {
        int(index)
        for index, label in id2label.items()
        if label.split("-", 1)[-1] in PERSON_MODEL_LABELS
    }


def _token_person_probabilities(text: str, analyzer) -> list[tuple[int, int, float]]:
    """Probabilidad de persona por token, sumando las cuatro etiquetas.

    Procesa el texto por ventanas solapadas para no truncar los documentos
    largos. Devuelve una lista de (inicio, fin, probabilidad). Lanza si el
    pipeline no permite obtener las probabilidades; el llamador cae a la
    puntuación del hallazgo.
    """
    pipe = get_token_pipeline(analyzer)
    encoding = pipe.tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=WINDOW_MAX_LENGTH,
        padding=True,
        stride=WINDOW_STRIDE,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        return_special_tokens_mask=True,
    )
    offsets = encoding.pop("offset_mapping").tolist()
    special_tokens = encoding.pop("special_tokens_mask").tolist()
    encoding.pop("overflow_to_sample_mapping", None)

    person_ids = _person_label_ids(pipe)
    by_span: dict[tuple[int, int], float] = {}
    for window in range(len(offsets)):
        window_inputs = {
            key: value[window : window + 1] for key, value in encoding.items()
        }
        window_inputs["sentence"] = text
        window_inputs["is_last"] = True
        window_inputs["offset_mapping"] = offsets[window]
        window_inputs["special_tokens_mask"] = special_tokens[window]

        # _forward necesita estos campos, igual que en el pipeline de Presidio.
        outputs = pipe.forward(window_inputs)
        logits = outputs["logits"][0].detach().cpu().numpy()
        shifted = np.exp(logits - logits.max(axis=-1, keepdims=True))
        probabilities = shifted / shifted.sum(axis=-1, keepdims=True)

        for index, (start, end) in enumerate(offsets[window]):
            if special_tokens[window][index] or start == end:
                continue
            probability = float(
                sum(probabilities[index][label_id] for label_id in person_ids)
            )
            # Las ventanas se solapan: se conserva la mayor probabilidad.
            by_span[(start, end)] = max(by_span.get((start, end), 0.0), probability)

    return [
        (start, end, probability)
        for (start, end), probability in sorted(by_span.items())
    ]


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


def _normalized_value(text: str, finding: Finding) -> str:
    return " ".join(text[finding.start : finding.end].split()).casefold()


def _same_data(text: str, first: Finding, second: Finding) -> bool:
    """Dos hallazgos son el mismo dato si comparten valor o son contiguos.

    Los fragmentos de un identificador troceado quedan pegados o separados
    solo por espacios o tabuladores. Un salto de línea o una puntuación
    separan datos distintos.
    """
    if first.entity_type != second.entity_type:
        return False
    if _normalized_value(text, first) == _normalized_value(text, second):
        return True
    earlier, later = sorted((first, second), key=lambda finding: finding.start)
    if later.start < earlier.end:
        return True
    gap = text[earlier.end : later.start]
    return all(character in " \t" for character in gap)


def _non_person_data_groups(text: str, findings: list[Finding]) -> list[list[int]]:
    parent = list(range(len(findings)))

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for index, finding in enumerate(findings):
        for other in range(index):
            if _same_data(text, findings[other], finding):
                parent[root(index)] = root(other)

    groups: dict[int, list[int]] = {}
    for index in range(len(findings)):
        groups.setdefault(root(index), []).append(index)
    return [groups[key] for key in sorted(groups, key=lambda key: min(groups[key]))]


def document_confidence(text: str, findings: list[Finding], analyzer) -> float:
    """Mínimo del mejor soporte de cada dato garantizado; 1,0 sin ninguno.

    Se agrupa por dato para que el troceado de un mismo valor en varios
    hallazgos no rebaje la confianza si alguna de las partes se detectó con
    seguridad, y para que dos datos distintos de la misma categoría cuenten
    por separado. Las cuatro etiquetas de persona son una sola categoría
    (ADR-013), pero cada persona distinta es un dato.
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

    supports: list[float] = []

    person_indices = [
        index
        for index, finding in enumerate(guaranteed)
        if finding.entity_type in PERSON_TYPES
    ]
    grouped_persons: set[int] = set()
    for group in group_person_findings(text, guaranteed):
        grouped_persons.update(group)
        if tokens is not None:
            support = max(
                _person_support(guaranteed[index], tokens) for index in group
            )
        else:
            support = max(guaranteed[index].score for index in group)
        supports.append(support)
    # Una persona sin nombre normalizable no se agrupa; cuenta como dato propio.
    for index in person_indices:
        if index not in grouped_persons:
            if tokens is not None:
                supports.append(_person_support(guaranteed[index], tokens))
            else:
                supports.append(guaranteed[index].score)

    non_person_indices = [
        index
        for index, finding in enumerate(guaranteed)
        if finding.entity_type not in PERSON_TYPES
    ]
    non_person_findings = [guaranteed[index] for index in non_person_indices]
    for group in _non_person_data_groups(text, non_person_findings):
        supports.append(
            max(non_person_findings[index].score for index in group)
        )

    return min(supports)
