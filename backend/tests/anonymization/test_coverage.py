"""Tests de las métricas de cobertura de la anonimización (ACO-037).

Cubren el filtro de categorías garantizadas, la fecha de nacimiento frente a
las fechas clínicas, el documento retenido y el ilegible, el objetivo y el
límite declarado, la ausencia de contenido, la reproducibilidad y los códigos
de salida. La trazabilidad está en `docs/aco/ACO-037.md`, sección 11.
"""

import json

import pytest

from app.services.anonymization import coverage
from app.services.anonymization.analyzer import build_analyzer
from app.services.anonymization.coverage import (
    FECHAS_CLINICAS,
    LIMITE_ADR_027,
    guaranteed_entities,
    main,
    measure_coverage,
    render,
)
from app.services.anonymization.models import (
    REASON_EMPTY_TEXT,
    REASON_LOW_CONFIDENCE,
    AnonymizationResult,
    AnonymizationStatus,
)
from app.services.anonymization.policy import POLICY
from app.services.anonymization.service import AnonymizationService
from tests.synthetic_data import load_document, load_manifest

BIRTH_DATE = "14/03/1958"

# Categorías garantizadas por ADR-013, escritas aquí y no tomadas de la
# función: es la lista que el test fija (AC-07).
GUARANTEED_CATEGORIES = {
    "PACIENTE",
    "PERSONAL_SANITARIO",
    "FAMILIAR",
    "PERSON",
    "ES_DNI",
    "ES_NIE",
    "ES_HISTORIA_CLINICA",
    "ID_ASEGURAMIENTO",
    "ID_CONTACTO_ASISTENCIAL",
    "ID_EMPLEO_PERSONAL_SANITARIO",
    "ID_TITULACION_PERSONAL_SANITARIO",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "CALLE",
}

# Entidades garantizadas de cada documento del corpus, con sus ocurrencias
# (ACO-037 §9): 8, 11 y 18. La lista se escribe en el test, no se deriva.
EXPECTED_GUARANTEED = {
    "informe_patologia_01.txt": {
        "7300451": 1,
        "12345678Z": 1,
        BIRTH_DATE: 1,
        "Inés Carrascal Ochoa": 2,
        "ALBENDEA QUINTANAR, ROSARIO": 1,
        "Andrés Lozoya Benítez": 1,
        "99/00123": 1,
    },
    "analitica_01.txt": {
        "7300451": 1,
        "12345678Z": 1,
        BIRTH_DATE: 1,
        "Inés Carrascal Ochoa": 1,
        "Rosario Albendea Quintanar": 1,
        "Fermín Ugarte Salcedo": 1,
        "TSI 0000 1234 5678": 1,
        "Calle del Almendro Florido, 14, 3.º B": 1,
        "600 123 456": 1,
        "PET-2026-000123": 1,
        "99/00456": 1,
    },
    "carta_oncologia_01.txt": {
        "7300451": 1,
        "12345678Z": 1,
        BIRTH_DATE: 1,
        "Inés Carrascal Ochoa": 1,
        "Rosario Albendea Quintanar": 1,
        "Albendea Quintanar": 2,
        "Tomás Ibarrola Senra": 1,
        "Andrés Lozoya Benítez": 1,
        "TSI 0000 1234 5678": 1,
        "Calle del Almendro Florido, 14, 3.º B": 1,
        "600 123 456": 1,
        "900 000 000": 2,
        "rosario.albendea@example.com": 1,
        "oncologia.monteluz@example.org": 2,
        "99/00789": 1,
    },
}


class FakeService:
    """Servicio falso: devuelve un resultado fijo por texto del documento."""

    def __init__(self, results):
        self.results = results
        self.calls = 0

    def anonymize(self, text):
        self.calls += 1
        return self.results[text]


def corpus():
    manifest = load_manifest()
    documents = {
        entry["file"]: load_document(entry["file"]) for entry in manifest["documents"]
    }
    return documents, manifest


def validated():
    return AnonymizationResult(
        status=AnonymizationStatus.VALIDADO,
        confidence=1.0,
        anonymized_text="",
        entities_count={},
    )


def retained():
    return AnonymizationResult(
        status=AnonymizationStatus.RETENIDO,
        confidence=0.5,
        anonymized_text=None,
        entities_count={},
        reason=REASON_LOW_CONFIDENCE,
    )


def illegible():
    return AnonymizationResult(
        status=AnonymizationStatus.ILEGIBLE,
        confidence=None,
        anonymized_text=None,
        entities_count={},
        reason=REASON_EMPTY_TEXT,
    )


def fake_service(documents, overrides=None):
    results = {text: validated() for text in documents.values()}
    for name, result in (overrides or {}).items():
        results[documents[name]] = result
    return FakeService(results)


def by_file(report):
    return {document["fichero"]: document for document in report["documentos"]}


def no_medido(report):
    return {item["categoria"]: item["motivo"] for item in report["no_medido"]}


def test_report_format_and_totals():
    documents, manifest = corpus()
    report = measure_coverage(
        fake_service(documents, {"analitica_01.txt": retained()}), documents, manifest
    )

    assert set(report) == {"documentos", "categorias", "total", "no_medido"}
    assert [d["fichero"] for d in report["documentos"]] == [
        entry["file"] for entry in manifest["documents"]
    ]

    documents_by_file = by_file(report)
    assert documents_by_file["informe_patologia_01.txt"] == {
        "fichero": "informe_patologia_01.txt",
        "estado": "validado",
        "motivo": None,
        "esperadas": 8,
        "cubiertas": 8,
    }
    assert documents_by_file["analitica_01.txt"] == {
        "fichero": "analitica_01.txt",
        "estado": "retenido",
        "motivo": REASON_LOW_CONFIDENCE,
        "esperadas": 11,
        "cubiertas": 0,
    }
    assert documents_by_file["carta_oncologia_01.txt"]["esperadas"] == 18
    assert documents_by_file["carta_oncologia_01.txt"]["cubiertas"] == 18

    total = report["total"]
    assert total["esperadas"] == 37
    assert total["cubiertas"] == 26
    assert total["cobertura"] == pytest.approx(26 / 37)
    assert total["objetivo"] == 0.85


def test_only_guaranteed_categories_are_measured():
    documents, manifest = corpus()
    report = measure_coverage(fake_service(documents), documents, manifest)

    categories = {item["categoria"]: item for item in report["categorias"]}
    assert set(categories) == {
        "PERSON",
        "ES_HISTORIA_CLINICA",
        "ES_DNI",
        "ID_TITULACION_PERSONAL_SANITARIO",
        "ID_ASEGURAMIENTO",
        "ID_CONTACTO_ASISTENCIAL",
        "PHONE_NUMBER",
        "EMAIL_ADDRESS",
        "CALLE",
        "FECHA_NACIMIENTO",
    }
    assert set(categories) <= GUARANTEED_CATEGORIES | {"FECHA_NACIMIENTO"}
    assert categories["PERSON"]["esperadas"] == 13
    assert categories["FECHA_NACIMIENTO"]["esperadas"] == 3
    assert categories["FECHA_NACIMIENTO"]["cubiertas"] == 3

    measured = no_medido(report)
    assert {"HOSPITAL", "TERRITORIO", "AGE", "SEXO", FECHAS_CLINICAS} <= set(measured)
    for category in ("HOSPITAL", "TERRITORIO", "AGE", "SEXO", FECHAS_CLINICAS):
        assert measured[category]

    # Las cuentas cuadran: 37 medidas y 41 no medidas son las 78 del manifiesto.
    unmeasured = sum(
        entity["count"]
        for document in manifest["documents"]
        for entity in document["entities"]
        if entity["category"] in {"HOSPITAL", "TERRITORIO", "AGE", "SEXO"}
        or (entity["category"] == "DATE_TIME" and entity["text"] != BIRTH_DATE)
    )
    assert unmeasured == 41
    assert report["total"]["esperadas"] + unmeasured == 78


def test_objective_limit_and_pending_figures():
    documents, manifest = corpus()
    report = measure_coverage(fake_service(documents), documents, manifest)

    assert report["total"]["objetivo"] == 0.85
    measured = no_medido(report)
    assert LIMITE_ADR_027 in measured.values()

    pending = [
        item
        for item in report["no_medido"]
        if "ACO-038" in item["motivo"] and "ACO-036" in item["motivo"]
    ]
    assert len(pending) == 2


def test_retained_and_illegible_count_as_not_covered():
    documents, manifest = corpus()
    service = fake_service(
        documents,
        {"analitica_01.txt": retained(), "carta_oncologia_01.txt": illegible()},
    )
    report = measure_coverage(service, documents, manifest)

    documents_by_file = by_file(report)
    assert documents_by_file["analitica_01.txt"]["estado"] == "retenido"
    assert documents_by_file["analitica_01.txt"]["cubiertas"] == 0
    assert documents_by_file["carta_oncologia_01.txt"]["estado"] == "ilegible"
    assert documents_by_file["carta_oncologia_01.txt"]["motivo"] == REASON_EMPTY_TEXT
    assert documents_by_file["carta_oncologia_01.txt"]["esperadas"] == 18
    assert documents_by_file["carta_oncologia_01.txt"]["cubiertas"] == 0


def test_coverage_is_null_without_expected_occurrences():
    text = "Hospital Universitario Monteluz"
    documents = {"doc.txt": text}
    manifest = {
        "documents": [
            {
                "file": "doc.txt",
                "entities": [
                    {
                        "text": text,
                        "category": "HOSPITAL",
                        "count": 1,
                    }
                ],
            }
        ]
    }
    report = measure_coverage(FakeService({text: validated()}), documents, manifest)

    assert report["categorias"] == []
    assert report["total"] == {
        "esperadas": 0,
        "cubiertas": 0,
        "cobertura": None,
        "objetivo": 0.85,
    }
    assert "n/a" in render(report)


def test_partial_occurrences_and_surviving_person_token():
    text = "Ana Pérez llamó. Ana Pérez llamó."
    documents = {"doc.txt": text}
    manifest = {
        "documents": [
            {
                "file": "doc.txt",
                "entities": [
                    {"text": "Ana Pérez", "category": "PERSON", "count": 2},
                    {"text": "12345678Z", "category": "ES_DNI", "count": 2},
                ],
            }
        ]
    }
    # Sobrevive un token significativo del nombre y una de las dos apariciones
    # del DNI: la persona cuenta como no cubierta y el DNI, a la mitad.
    result = AnonymizationResult(
        status=AnonymizationStatus.VALIDADO,
        confidence=1.0,
        anonymized_text="Pérez 12345678Z [PERSONA]",
        entities_count={},
    )
    report = measure_coverage(FakeService({text: result}), documents, manifest)

    categories = {item["categoria"]: item for item in report["categorias"]}
    assert categories["PERSON"]["esperadas"] == 2
    assert categories["PERSON"]["cubiertas"] == 0
    assert categories["ES_DNI"]["esperadas"] == 2
    assert categories["ES_DNI"]["cubiertas"] == 1
    assert report["total"]["cubiertas"] == 1


def test_report_contains_no_document_content():
    documents, manifest = corpus()
    report = measure_coverage(
        fake_service(documents, {"analitica_01.txt": retained()}), documents, manifest
    )

    serialized = json.dumps(report, ensure_ascii=False)
    rendered = render(report)
    for document in manifest["documents"]:
        for entity in document["entities"]:
            assert entity["text"] not in serialized
            assert entity["text"] not in rendered
        for line in load_document(document["file"]).splitlines():
            line = line.strip()
            if line:
                assert line not in serialized
                assert line not in rendered


def test_report_is_reproducible():
    documents, manifest = corpus()
    first = measure_coverage(fake_service(documents), documents, manifest)
    second = measure_coverage(fake_service(documents), documents, manifest)

    assert first == second
    assert json.dumps(first) == json.dumps(second)


def test_guaranteed_entities_match_the_fixed_list():
    assert {t for t, p in POLICY.items() if p.guaranteed} == GUARANTEED_CATEGORIES

    manifest = load_manifest()
    for document in manifest["documents"]:
        name = document["file"]
        result = list(guaranteed_entities(document["entities"], load_document(name)))
        assert {entity["text"]: entity["count"] for entity in result} == (
            EXPECTED_GUARANTEED[name]
        )
        assert sum(entity["count"] for entity in result) == sum(
            EXPECTED_GUARANTEED[name].values()
        )
        for entity in result:
            assert entity["category"] in GUARANTEED_CATEGORIES or (
                entity["category"] == "DATE_TIME" and entity["text"] == BIRTH_DATE
            )


@pytest.fixture(scope="module")
def model_service():
    # Fixture propio: el `model_service` de `test_service.py` no se comparte.
    return AnonymizationService(analyzer=build_analyzer())


def test_real_corpus_statuses(model_service):
    documents, manifest = corpus()
    report = measure_coverage(model_service, documents, manifest)

    statuses = {document["fichero"]: document["estado"] for document in report["documentos"]}
    assert statuses == {
        "informe_patologia_01.txt": "validado",
        "analitica_01.txt": "retenido",
        "carta_oncologia_01.txt": "validado",
    }
    retained = by_file(report)["analitica_01.txt"]
    assert retained["esperadas"] == 11
    assert retained["cubiertas"] == 0
    assert retained["motivo"] == REASON_LOW_CONFIDENCE
    assert report["total"]["esperadas"] == 37
    assert 0 < report["total"]["cobertura"] < 1


def test_main_emits_the_report(monkeypatch, capsys):
    documents, _ = corpus()
    monkeypatch.setattr(coverage, "AnonymizationService", lambda: fake_service(documents))

    assert main() == 0

    captured = capsys.readouterr()
    assert "documentos:" in captured.out
    assert "categorias:" in captured.out
    assert "total:" in captured.out
    assert "objetivo=0.85" in captured.out
    assert captured.err == ""


def test_main_returns_two_for_an_unreadable_manifest(tmp_path, capsys):
    missing = tmp_path / "no-existe.json"

    assert main(manifest_path=missing) == 2

    captured = capsys.readouterr()
    assert str(missing) in captured.err
    assert captured.out == ""


def test_main_returns_two_for_an_unreadable_document(tmp_path, capsys):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"documents": [{"file": "falta.txt", "entities": []}]}),
        encoding="utf-8",
    )

    assert main(corpus_dir=documents_dir, manifest_path=manifest) == 2

    captured = capsys.readouterr()
    assert "falta.txt" in captured.err
    assert captured.out == ""


def test_main_returns_two_for_invalid_json(tmp_path, capsys):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{", encoding="utf-8")

    assert main(manifest_path=manifest) == 2

    captured = capsys.readouterr()
    assert str(manifest) in captured.err
    assert captured.out == ""
