"""Métricas de cobertura de la anonimización (ACO-037).

Comando de diagnóstico: mide sobre el corpus sintético de ACO-051 cuántas
ocurrencias de las categorías que ADR-013 garantiza sobreviven a la
anonimización. No lo importa la API, no persiste nada y no escribe contenido:
el único dato del corpus que publica es el nombre del fichero.

Se ejecuta desde `backend/`:

    python -m app.services.anonymization.coverage
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import OrderedDict
from pathlib import Path

from .detection import Detection
from .models import AnonymizationStatus
from .policy import PERSON_TYPES, POLICY, is_birth_date
from .service import AnonymizationService

# Objetivo de cobertura de la Arquitectura §4: superior al 85 % en los
# Niveles 1–2. Es un objetivo del módulo, no un umbral que tumbe la CI.
OBJETIVO = 0.85

# Límite de medición de ADR-027 §9, literal (ficha, §8.5).
LIMITE_ADR_027 = "identificación por combinación: no se mide (ADR-027 §9)"

# Categorías que no cuentan como cobertura y su motivo (ADR-013; ACO-023 P5).
NO_MEDIDO = {
    "HOSPITAL": "se anonimiza si se detecta, sin garantía (ADR-013)",
    "CENTRO_SALUD": "se anonimiza si se detecta, sin garantía (ADR-013)",
    "INSTITUCION": "se anonimiza si se detecta, sin garantía (ADR-013)",
    "TERRITORIO": "la etiqueta mezcla localidad y provincia (ACO-023 P5)",
    "AGE": "contexto clínico que no se anonimiza (ADR-013)",
    "SEXO": "contexto clínico que no se anonimiza (ADR-013)",
    "PROFESION": "contexto clínico que no se anonimiza (ADR-013)",
    "PAIS": "contexto clínico que no se anonimiza (ADR-013)",
}
FECHAS_CLINICAS = "DATE_TIME (fechas clínicas)"
FECHAS_CLINICAS_MOTIVO = "fechas que no son de nacimiento (ADR-013)"

# Las dos cifras de marcas de ADR-027 §8: asignadas a ACO-037, sin datos hasta
# que existan el esquema de ACO-038 y las filas del Nivel 3 (ACO-036).
MARCAS = (
    "marcas totales",
    "marcas sobre términos de ADR-013",
)
MARCAS_MOTIVO = "ADR-027 §8: sin datos hasta ACO-038 y ACO-036"

# Mismas comprobaciones que T-31 (ACO-026 §8.3): los identificadores se buscan
# por su secuencia de dígitos y los textos por su forma normalizada.
IDENTIFIER_CATEGORIES = {
    "ES_DNI",
    "ES_NIE",
    "ES_HISTORIA_CLINICA",
    "ID_ASEGURAMIENTO",
    "ID_CONTACTO_ASISTENCIAL",
    "ID_EMPLEO_PERSONAL_SANITARIO",
    "ID_TITULACION_PERSONAL_SANITARIO",
    "PHONE_NUMBER",
}
TEXT_CATEGORIES = {"EMAIL_ADDRESS", "CALLE"}


def guaranteed_entities(entities, original_text):
    """Entidades del manifiesto que ADR-013 garantiza (ACO-026 §8.2).

    Se deriva de la política de ACO-023 y no de una lista literal. `DATE_TIME`
    cuenta solo si `is_birth_date()` lo reconoce sobre el documento original;
    el manifiesto no trae posiciones, así que se usa la primera aparición del
    texto, como en `test_service.py`.
    """
    for entity in entities:
        policy = POLICY.get(entity["category"])
        if policy is not None and policy.guaranteed:
            yield entity
        elif entity["category"] == "DATE_TIME" and _is_birth_date(entity, original_text):
            yield entity


def _is_birth_date(entity, original_text):
    value = entity["text"]
    try:
        start = original_text.index(value)
    except ValueError:
        return False
    detection = Detection("DATE_TIME", start, start + len(value), 1.0)
    return is_birth_date(original_text, detection)


def _category_of(entity):
    """Etiqueta de la categoría medida; la fecha de nacimiento se nombra aparte."""
    if entity["category"] == "DATE_TIME":
        return "FECHA_NACIMIENTO"
    return entity["category"]


def _normalize(value):
    decomposed = unicodedata.normalize("NFKD", value)
    without_marks = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return " ".join(without_marks.casefold().split())


def _contains_word(haystack, needle):
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack) is not None


def _count_word(value, text):
    return len(re.findall(rf"(?<!\w){re.escape(value)}(?!\w)", text))


def _surviving_occurrences(entity, anonymized_text):
    """Ocurrencias del valor que sobreviven al texto anonimizado."""
    value = entity["text"]
    category = entity["category"]
    if category in IDENTIFIER_CATEGORIES:
        digits = re.sub(r"\D", "", value)
        if digits:
            return re.sub(r"\D", "", anonymized_text).count(digits)
    if category in TEXT_CATEGORIES or category == "DATE_TIME":
        if _normalize(value) in _normalize(anonymized_text):
            return entity["count"]
    return _count_word(value, anonymized_text)


def _person_survives(value, anonymized_text):
    """Un token significativo del nombre que sobrevive deja la entidad sin cubrir."""
    if _count_word(value, anonymized_text):
        return True
    normalized = _normalize(anonymized_text)
    return any(
        _contains_word(normalized, _normalize(token))
        for token in re.findall(r"[^\W\d_]{4,}", value)
    )


def _covered_occurrences(entity, anonymized_text):
    expected = entity["count"]
    if entity["category"] in PERSON_TYPES:
        return 0 if _person_survives(entity["text"], anonymized_text) else expected
    return expected - min(expected, _surviving_occurrences(entity, anonymized_text))


def _ratio(covered, expected):
    return None if expected == 0 else covered / expected


def measure_coverage(service, documents, manifest):
    """Devuelve el informe de cobertura de §8.1 de la ficha.

    `documents` es un diccionario nombre → texto y `manifest` el de ACO-051.
    Un documento retenido o ilegible suma a `esperadas` y no a `cubiertas`.
    """
    documentos = []
    categorias = OrderedDict()
    no_medido = OrderedDict()
    total_esperadas = 0
    total_cubiertas = 0

    for entry in manifest["documents"]:
        name = entry["file"]
        original = documents[name]
        result = service.anonymize(original)
        validated = (
            result.status is AnonymizationStatus.VALIDADO
            and result.anonymized_text is not None
        )
        anonymized = result.anonymized_text or ""

        doc_esperadas = 0
        doc_cubiertas = 0
        for entity in guaranteed_entities(entry["entities"], original):
            expected = entity["count"]
            covered = _covered_occurrences(entity, anonymized) if validated else 0
            doc_esperadas += expected
            doc_cubiertas += covered
            bucket = categorias.setdefault(_category_of(entity), [0, 0])
            bucket[0] += expected
            bucket[1] += covered

        for entity in entry["entities"]:
            category = entity["category"]
            if category == "DATE_TIME":
                if not _is_birth_date(entity, original):
                    no_medido[FECHAS_CLINICAS] = FECHAS_CLINICAS_MOTIVO
                continue
            policy = POLICY.get(category)
            if policy is None or not policy.guaranteed:
                no_medido[category] = NO_MEDIDO.get(
                    category, "no garantizada (ADR-013)"
                )

        documentos.append(
            {
                "fichero": name,
                "estado": result.status.value,
                "motivo": result.reason,
                "esperadas": doc_esperadas,
                "cubiertas": doc_cubiertas,
            }
        )
        total_esperadas += doc_esperadas
        total_cubiertas += doc_cubiertas

    report = {
        "documentos": documentos,
        "categorias": [
            {
                "categoria": category,
                "esperadas": esperadas,
                "cubiertas": cubiertas,
                "cobertura": _ratio(cubiertas, esperadas),
            }
            for category, (esperadas, cubiertas) in categorias.items()
        ],
        "total": {
            "esperadas": total_esperadas,
            "cubiertas": total_cubiertas,
            "cobertura": _ratio(total_cubiertas, total_esperadas),
            "objetivo": OBJETIVO,
        },
        "no_medido": [
            {"categoria": category, "motivo": motivo}
            for category, motivo in no_medido.items()
        ],
    }
    report["no_medido"].append(
        {"categoria": "límite de medición", "motivo": LIMITE_ADR_027}
    )
    for marca in MARCAS:
        report["no_medido"].append({"categoria": marca, "motivo": MARCAS_MOTIVO})
    return report


def _format_ratio(value):
    return "n/a" if value is None else f"{value:.3f}"


def render(report):
    """Texto legible del informe, sin contenido y sin rutas absolutas."""
    lines = ["documentos:"]
    for doc in report["documentos"]:
        line = (
            f"  {doc['fichero']}  {doc['estado']}  "
            f"esperadas={doc['esperadas']} cubiertas={doc['cubiertas']} "
            f"sobreviven={doc['esperadas'] - doc['cubiertas']}"
        )
        if doc["motivo"]:
            line += f"  motivo={doc['motivo']}"
        lines.append(line)
    lines.append("categorias:")
    for category in report["categorias"]:
        lines.append(
            f"  {category['categoria']}  esperadas={category['esperadas']} "
            f"cubiertas={category['cubiertas']} "
            f"cobertura={_format_ratio(category['cobertura'])}"
        )
    total = report["total"]
    lines.append(
        f"total: esperadas={total['esperadas']} cubiertas={total['cubiertas']} "
        f"sobreviven={total['esperadas'] - total['cubiertas']} "
        f"cobertura={_format_ratio(total['cobertura'])} "
        f"objetivo={total['objetivo']} (superior al 85 %)"
    )
    lines.append("no_medido:")
    for item in report["no_medido"]:
        lines.append(f"  {item['categoria']} — {item['motivo']}")
    return "\n".join(lines)


def _load_corpus(corpus_dir=None, manifest_path=None):
    """Carga documentos y manifiesto; por defecto, los de ACO-051.

    El import de `tests.synthetic_data` vive aquí y no al importar el módulo:
    así `coverage.py` se puede importar sin el paquete de tests.
    """
    from tests.synthetic_data import (
        DOCUMENTS_DIR,
        MANIFEST_PATH,
        load_document,
        load_manifest,
    )

    if corpus_dir is None and manifest_path is None:
        manifest = load_manifest()
        documents = {
            entry["file"]: load_document(entry["file"])
            for entry in manifest["documents"]
        }
        return documents, manifest

    manifest_file = Path(manifest_path) if manifest_path is not None else MANIFEST_PATH
    documents_dir = Path(corpus_dir) if corpus_dir is not None else DOCUMENTS_DIR
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    documents = {
        entry["file"]: (documents_dir / entry["file"]).read_text(encoding="utf-8")
        for entry in manifest["documents"]
    }
    return documents, manifest


def main(corpus_dir=None, manifest_path=None):
    """Emite el informe; 0 si se emite y 2 si no se puede leer la entrada."""
    try:
        documents, manifest = _load_corpus(corpus_dir, manifest_path)
    except (OSError, ValueError, KeyError, TypeError) as error:
        location = manifest_path or corpus_dir
        prefix = (
            f"error: no se pudo leer {location}: "
            if location is not None
            else "error: no se pudo leer el corpus o el manifiesto: "
        )
        print(prefix + str(error), file=sys.stderr)
        return 2

    report = measure_coverage(AnonymizationService(), documents, manifest)
    print(render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
