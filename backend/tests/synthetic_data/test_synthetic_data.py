import json
import re

import pytest

from app.services.anonymization.analyzer import DEFAULT_ENTITIES, MEDDOCAN_ENTITY_MAPPING
from tests.synthetic_data import (
    DOCUMENTS_DIR,
    MANIFEST_PATH,
    count_occurrences,
    load_document,
    load_manifest,
)

EXPECTED_DOCUMENTS = [
    "informe_patologia_01.txt",
    "analitica_01.txt",
    "carta_oncologia_01.txt",
]

KNOWN_ENTITY_TYPES = set(DEFAULT_ENTITIES) | set(MEDDOCAN_ENTITY_MAPPING.values())

REQUIRED_CATEGORIES = {
    "PERSON",
    "DATE_TIME",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "ES_DNI",
    "ES_HISTORIA_CLINICA",
    "ID_ASEGURAMIENTO",
    "CALLE",
    "HOSPITAL",
    "TERRITORIO",
}

RESERVED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}
ALLOWED_DNI = {"12345678Z", "87654321X", "00000000T"}
ALLOWED_PHONES = {"600 123 456", "900 000 000"}

SHARED_ENTITIES = [
    "7300451",
    "12345678Z",
    "14/03/1958",
    "Hospital Universitario Monteluz",
]

EMAIL_PATTERN = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")
DNI_PATTERN = re.compile(r"(?<!\w)\d{8}[A-Za-z](?!\w)")


def manifest_entries():
    return load_manifest()["documents"]


def all_entities():
    return [entity for entry in manifest_entries() for entity in entry["entities"]]


@pytest.mark.parametrize("name", EXPECTED_DOCUMENTS)
def test_document_exists_is_utf8_and_not_empty(name):
    path = DOCUMENTS_DIR / name

    assert path.is_file()
    assert path.read_bytes().decode("utf-8").strip()


@pytest.mark.parametrize("name", EXPECTED_DOCUMENTS)
def test_document_has_between_250_and_700_words(name):
    words = len(load_document(name).split())

    assert 250 <= words <= 700


def test_manifest_is_valid_json_and_references_existing_documents():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    files = [entry["file"] for entry in manifest["documents"]]

    assert sorted(files) == sorted(EXPECTED_DOCUMENTS)
    for entry in manifest["documents"]:
        assert (DOCUMENTS_DIR / entry["file"]).is_file()
        assert entry["type"]
        assert entry["entities"]


def test_each_entity_appears_exactly_count_times():
    for entry in manifest_entries():
        text = load_document(entry["file"])

        for entity in entry["entities"]:
            assert entity["count"] >= 1, entity
            assert count_occurrences(entity["text"], text) == entity["count"], (
                entry["file"],
                entity,
            )


def test_entity_texts_are_unique_per_document():
    for entry in manifest_entries():
        texts = [entity["text"] for entity in entry["entities"]]

        assert len(texts) == len(set(texts)), entry["file"]


def test_each_category_is_a_known_entity_type():
    for entity in all_entities():
        assert entity["category"] in KNOWN_ENTITY_TYPES, entity


def test_required_categories_are_covered():
    categories = {entity["category"] for entity in all_entities()}

    assert REQUIRED_CATEGORIES <= categories


def test_emails_use_reserved_domains_and_are_listed():
    for entry in manifest_entries():
        text = load_document(entry["file"])
        listed = {entity["text"] for entity in entry["entities"]}

        for match in EMAIL_PATTERN.finditer(text):
            assert match.group(1).lower() in RESERVED_EMAIL_DOMAINS, match.group(0)
            assert match.group(0) in listed, match.group(0)


def test_dnis_are_allowed_and_listed():
    for entry in manifest_entries():
        text = load_document(entry["file"])
        listed = {entity["text"] for entity in entry["entities"]}

        for dni in DNI_PATTERN.findall(text):
            assert dni in ALLOWED_DNI, dni
            assert dni in listed, dni


def test_phones_follow_evident_patterns():
    phones = {
        entity["text"]
        for entity in all_entities()
        if entity["category"] == "PHONE_NUMBER"
    }

    assert phones
    assert phones <= ALLOWED_PHONES


def test_same_patient_data_in_all_documents():
    for entry in manifest_entries():
        listed = {entity["text"] for entity in entry["entities"]}

        for shared in SHARED_ENTITIES:
            assert shared in listed, (entry["file"], shared)


def test_partial_patient_mention_is_listed():
    texts = {entity["text"] for entity in all_entities()}

    assert "Albendea Quintanar" in texts


def test_clinical_content_supports_conversation():
    corpus = " ".join(load_document(name) for name in EXPECTED_DOCUMENTS).lower()

    for keyword in ["adenocarcinoma", "estadio iii", "ca 19-9", "folfirinox"]:
        assert keyword in corpus, keyword


def test_load_functions_return_text_and_manifest():
    text = load_document("analitica_01.txt")
    manifest = load_manifest()

    assert isinstance(text, str)
    assert "CA 19-9" in text
    assert isinstance(manifest, dict)
    assert isinstance(manifest["documents"], list)


@pytest.mark.parametrize("name", ["no_existe.txt", "../expected_entities.json", ""])
def test_load_document_rejects_unknown_or_path_names(name):
    with pytest.raises((FileNotFoundError, ValueError)):
        load_document(name)
