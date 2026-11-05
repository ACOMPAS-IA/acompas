"""Etiquetas, numeración y sustitución del texto (ACO-023).

Las etiquetas de persona siguen ACO-022 (B4) y se numeran por documento. La
agrupación reutiliza la normalización de nombres de ACO-022 y sus reglas
básicas: mismo nombre, o mención parcial de dos o más palabras contenida en
un único nombre completo. La agrupación es pública porque la confianza por
dato de ACO-023 la reutiliza.
"""

from collections import Counter

from .detection import normalize_name
from .policy import PERSON_TYPES, Finding, label_for


def group_person_findings(text: str, findings: list[Finding]) -> list[list[int]]:
    person_indices = [
        index
        for index, finding in enumerate(findings)
        if finding.entity_type in PERSON_TYPES
    ]
    names = {
        index: normalize_name(text[findings[index].start : findings[index].end])
        for index in person_indices
    }

    groups: list[list[int]] = []
    by_name: dict[tuple[str, ...], int] = {}
    for index in person_indices:
        name = names[index]
        if not name:
            continue
        if name in by_name:
            groups[by_name[name]].append(index)
        else:
            by_name[name] = len(groups)
            groups.append([index])

    # Una mención parcial (dos o más palabras) se une a la única mención
    # completa que la contiene. Las de una palabra no se agrupan (ACO-022, B9,
    # regla 5).
    parent = list(range(len(groups)))

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for index, group in enumerate(groups):
        name = set(names[group[0]])
        if len(name) < 2:
            continue
        candidates = [
            other
            for other, other_group in enumerate(groups)
            if other != index and name < set(names[other_group[0]])
        ]
        if len(candidates) == 1:
            parent[index] = root(candidates[0])

    merged: dict[int, list[int]] = {}
    for index, group in enumerate(groups):
        merged.setdefault(root(index), []).extend(group)

    # Los grupos se ordenan por la primera mención, no por cuándo se crearon.
    return sorted(merged.values(), key=min)


def _group_type(findings: list[Finding], group: list[int]) -> str:
    types = {findings[index].entity_type for index in group}
    if len(types) == 1:
        return types.pop()
    # Si ACO-022 dejó roles distintos en el mismo nombre, se usa la etiqueta
    # genérica para no atribuir un rol erróneo.
    return "PERSON"


def _person_labels(
    text: str, findings: list[Finding]
) -> dict[int, str]:
    groups = group_person_findings(text, findings)
    grouped = {index for group in groups for index in group}
    # Una persona sin nombre normalizable (un tratamiento suelto o un fragmento
    # sin palabras) no se agrupa, pero sigue siendo un dato y recibe su número
    # propio (ficha, P12 y AC-11).
    groups = sorted(
        groups
        + [
            [index]
            for index, finding in enumerate(findings)
            if finding.entity_type in PERSON_TYPES and index not in grouped
        ],
        key=min,
    )
    labels: dict[int, str] = {}

    patients = [group for group in groups if _group_type(findings, group) == "PACIENTE"]
    counters: dict[str, int] = {}

    for group in groups:
        group_type = _group_type(findings, group)
        if group_type == "PACIENTE":
            if len(patients) == 1:
                label = "[PACIENTE]"
            else:
                number = patients.index(group) + 1
                label = f"[PACIENTE_{number}]"
        else:
            counters[group_type] = counters.get(group_type, 0) + 1
            label = {
                "PERSONAL_SANITARIO": f"[SANITARIO_{counters[group_type]}]",
                "FAMILIAR": f"[FAMILIAR_{counters[group_type]}]",
                "PERSON": f"[PERSONA_{counters[group_type]}]",
            }[group_type]
        for index in group:
            labels[index] = label

    return labels


def assign_labels(text: str, findings: list[Finding]) -> list[str]:
    """Devuelve una etiqueta por hallazgo, en el mismo orden que `findings`."""
    person_labels = _person_labels(text, findings)
    return [
        person_labels.get(index, label_for(finding))
        for index, finding in enumerate(findings)
    ]


def substitute(text: str, findings: list[Finding], labels: list[str]) -> str:
    """Sustituye de derecha a izquierda para no desplazar las posiciones."""
    ordered = sorted(
        zip(findings, labels), key=lambda item: item[0].start, reverse=True
    )
    anonymized = text
    for finding, label in ordered:
        anonymized = anonymized[: finding.start] + label + anonymized[finding.end :]
    return anonymized


def count_entities(findings: list[Finding]) -> dict[str, int]:
    return dict(Counter(finding.entity_type for finding in findings))
