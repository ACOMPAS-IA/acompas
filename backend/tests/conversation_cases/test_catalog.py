"""Tests estructurales del catálogo (ACO-052, AC-01 y AC-02).

Sin red, sin modelos y sin servicios externos.
"""

import json
import re

import pytest
from pydantic import ValidationError

from app.services.prompts import DOCUMENT_CLOSE_TAG
from tests.conversation_cases import (
    CATALOG_PATH,
    DOCUMENTS_DIR,
    GROUPS,
    Catalog,
    build_request,
    document_names,
    load_case_document,
    load_catalog,
)
from tests.synthetic_data import DOCUMENTS_DIR as SYNTHETIC_DOCUMENTS_DIR

CATALOG = load_catalog()
CASE_IDS = [case.id for case in CATALOG.cases]

# Grupo, documentos y modos de cada caso (ficha, sección 8.2). C15 está en
# «consulta» por decisión del responsable: comprueba el origen de la respuesta,
# no el aviso.
EXPECTED = {
    "C01": ("consulta", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C02": ("consulta", ["informe_patologia_01.txt"], ["api", "demo"]),
    "C03": ("consulta", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C04": ("consulta", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C05": ("consulta", ["informe_patologia_01.txt", "carta_oncologia_01.txt"], ["api"]),
    "C06": ("alcance", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C07": ("alcance", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C08": ("alcance", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C09": ("alcance", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C10": ("seguridad", ["carta_oncologia_inyeccion_01.txt"], ["api", "demo"]),
    "C11": ("seguridad", ["carta_oncologia_inyeccion_02.txt"], ["api", "demo"]),
    "C12": ("seguridad", ["carta_oncologia_01.txt"], ["api", "demo"]),
    "C13": ("seguridad", ["carta_oncologia_01.txt"], ["api"]),
    "C14": ("aviso", ["carta_oncologia_01.txt"], ["demo"]),
    "C15": ("consulta", ["carta_oncologia_01.txt"], ["api", "demo"]),
}


def raw_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def valid_case(**changes):
    case = raw_catalog()["cases"][0]
    case.update(changes)
    return case


# AC-01 — Catálogo válido


def test_catalog_loads():
    assert isinstance(CATALOG, Catalog)
    assert CATALOG.version == 1


def test_ids_are_unique():
    assert len(CASE_IDS) == len(set(CASE_IDS))


def test_duplicated_id_is_rejected():
    data = raw_catalog()
    data["cases"].append(data["cases"][0])
    with pytest.raises(ValidationError):
        Catalog.model_validate(data)


@pytest.mark.parametrize(
    "changes",
    [
        {"group": "otro"},
        {"id": "X01"},
        {"title": ""},
        {"must": []},
        {"must": ["  "]},
        {"documents": []},
        {"documents": ["a.txt", "b.txt", "c.txt", "d.txt"]},
        {"documents": ["../synthetic_data/documents/carta_oncologia_01.txt"]},
        {"documents": ["../cases.json"]},
        {"documents": ["/etc/passwd"]},
        {"documents": ["documents/carta_oncologia_inyeccion_01.txt"]},
        {"documents": [""]},
        {"documents": ["carta_oncologia_01.txt", "carta_oncologia_01.txt"]},
        {"modes": []},
        {"modes": ["ci"]},
        {"modes": ["api", "api"]},
        {"modes": ["api", "ci"]},
        {"refs": []},
        {"messages": []},
        {"messages": [{"role": "system", "content": "hola"}]},
        {"unexpected": True},
    ],
)
def test_invalid_case_is_rejected(changes):
    data = {"version": 1, "cases": [valid_case(**changes)]}
    with pytest.raises(ValidationError):
        Catalog.model_validate(data)


@pytest.mark.parametrize("version", [0, 2, "1", None])
def test_invalid_version_is_rejected(version):
    data = raw_catalog()
    data["version"] = version
    with pytest.raises(ValidationError):
        Catalog.model_validate(data)


def test_missing_version_is_rejected():
    data = raw_catalog()
    del data["version"]
    with pytest.raises(ValidationError):
        Catalog.model_validate(data)


def test_unknown_top_level_field_is_rejected():
    data = raw_catalog()
    data["extra"] = 1
    with pytest.raises(ValidationError):
        Catalog.model_validate(data)


@pytest.mark.parametrize("case", CATALOG.cases, ids=CASE_IDS)
def test_case_groups_are_valid(case):
    assert case.group in GROUPS


@pytest.mark.parametrize("case", CATALOG.cases, ids=CASE_IDS)
def test_case_has_must_and_valid_document_count(case):
    assert case.must
    assert 1 <= len(case.documents) <= 3


@pytest.mark.parametrize("case", CATALOG.cases, ids=CASE_IDS)
def test_case_documents_exist(case):
    for name in case.documents:
        assert name in document_names()
        assert load_case_document(name).strip()


@pytest.mark.parametrize("case", CATALOG.cases, ids=CASE_IDS)
def test_case_is_a_valid_conversation_request(case):
    texts = [load_case_document(name) for name in case.documents]

    request = build_request(case, texts)

    assert [document.text for document in request.documents] == texts
    assert request.messages[-1].role == "user"


def test_conversation_rules_are_enforced_by_the_loader():
    # Termina en assistant: no cumple el contrato de ACO-030.
    case = CATALOG.by_id("C13").model_copy(
        update={"messages": CATALOG.by_id("C13").messages[:2]}
    )
    with pytest.raises(ValidationError):
        build_request(case, [load_case_document("carta_oncologia_01.txt")])


def test_missing_document_is_reported(tmp_path):
    data = {"version": 1, "cases": [valid_case(documents=["no_existe.txt"])]}
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        load_catalog(path)


@pytest.mark.parametrize("name", ["", "../cases.json", "documents/x.txt", "/etc/passwd"])
def test_load_case_document_rejects_paths(name):
    with pytest.raises(ValueError):
        load_case_document(name)


def test_document_names_do_not_collide_between_folders():
    own = {path.name for path in DOCUMENTS_DIR.glob("*.txt")}
    synthetic = {path.name for path in SYNTHETIC_DOCUMENTS_DIR.glob("*.txt")}
    assert own and synthetic
    assert not own & synthetic


# AC-02 — Cobertura


def test_catalog_contains_exactly_c01_to_c15():
    assert CASE_IDS == [f"C{number:02d}" for number in range(1, 16)]


@pytest.mark.parametrize("case_id", EXPECTED)
def test_case_matches_section_8_2(case_id):
    case = CATALOG.by_id(case_id)
    group, documents, modes = EXPECTED[case_id]
    assert (case.group, case.documents, case.modes) == (group, documents, modes)


def test_all_groups_are_represented():
    assert {case.group for case in CATALOG.cases} == set(GROUPS)


def test_api_cases_are_computed_from_the_catalog():
    api_cases = CATALOG.with_mode("api")
    assert [case.id for case in api_cases] == [
        case.id for case in CATALOG.cases if "api" in case.modes
    ]
    assert "C14" not in {case.id for case in api_cases}
    assert api_cases


def test_aco_029_probes_s1_to_s9_are_covered():
    probes = set()
    for case in CATALOG.cases:
        for ref in case.refs:
            if ref.startswith("ACO-029"):
                probes.update(re.findall(r"\bS([1-9])\b", ref))
    assert probes == {str(number) for number in range(1, 10)}


def test_delimiter_case_c11_uses_a_false_closing_tag():
    case = CATALOG.by_id("C11")
    assert case.group == "seguridad"
    [name] = case.documents
    assert DOCUMENT_CLOSE_TAG in load_case_document(name)


def test_manipulated_history_case_c13():
    case = CATALOG.by_id("C13")
    assert [message.role for message in case.messages] == ["user", "assistant", "user"]


def test_aviso_group_is_c14_only():
    assert [case.id for case in CATALOG.cases if case.group == "aviso"] == ["C14"]


def test_c14_repeats_the_question_of_c01():
    assert CATALOG.by_id("C14").messages == CATALOG.by_id("C01").messages


@pytest.mark.parametrize("case", CATALOG.cases, ids=CASE_IDS)
def test_no_conversational_case_uses_the_retained_analysis(case):
    # La anonimización retiene analitica_01.txt (ACO-023, §8.7): se usa en F02.
    assert "analitica_01.txt" not in case.documents
