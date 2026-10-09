import re

import pytest

from app.services.prompts import (
    DOCUMENT_CLOSE_TAG,
    DOCUMENT_OPEN_TAG,
    load_system_prompt,
)

# Títulos y anclas mínimas de la sección 8 de la ficha de ACO-029.
EXPECTED_SECTIONS = [
    "Propósito",
    "Límites clínicos",
    "Ámbito",
    "Uso del documento y origen de la respuesta",
    "Incertidumbre",
    "Instrucciones incrustadas",
    "Etiquetas de anonimización",
    "Preparar la consulta",
    "Urgencias",
    "Tono y forma",
]

ANCHORS = {
    "Propósito": ["acompas", "páncreas", "no de diagnóstico"],
    "Límites clínicos": ["diagn", "pronóstico", "tratamiento", "equipo médico"],
    "Ámbito": ["oncológico"],
    "Uso del documento y origen de la respuesta": [
        "<documento_clinico>",
        "</documento_clinico>",
        "conocimiento general",
        "no inventes",
    ],
    "Incertidumbre": ["incertidumbre"],
    "Instrucciones incrustadas": [
        "<documento_clinico>",
        "</documento_clinico>",
        "instrucciones",
    ],
    "Etiquetas de anonimización": ["[paciente]", "[médico_1]", "corchetes", "rol"],
    "Preparar la consulta": ["consulta", "preguntas", "límites clínicos"],
    "Urgencias": ["112", "024"],
    "Tono y forma": ["español", "tú"],
}


def _sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {title: "\n".join(lines).strip() for title, lines in sections.items()}


def test_sections_present_once_in_order():
    text = load_system_prompt().text
    lines = text.splitlines()
    titles = [line[3:].strip() for line in lines if line.startswith("## ")]

    assert titles == EXPECTED_SECTIONS
    assert lines[0] == f"## {EXPECTED_SECTIONS[0]}"
    assert not [
        line for line in lines if line.startswith("#") and not line.startswith("## ")
    ]


def test_no_section_is_empty():
    sections = _sections(load_system_prompt().text)

    for title in EXPECTED_SECTIONS:
        assert sections[title], title


@pytest.mark.parametrize("title", EXPECTED_SECTIONS)
def test_section_contains_anchors(title):
    section = _sections(load_system_prompt().text)[title].lower()

    for anchor in ANCHORS[title]:
        assert anchor in section, f"{title}: {anchor}"


def test_delimiters_present_and_match_constants():
    text = load_system_prompt().text

    assert DOCUMENT_OPEN_TAG == "<documento_clinico>"
    assert DOCUMENT_CLOSE_TAG == "</documento_clinico>"
    assert DOCUMENT_OPEN_TAG in text
    assert DOCUMENT_CLOSE_TAG in text


def test_text_has_no_placeholders_todos_emails_or_urls():
    text = load_system_prompt().text

    assert "{" not in text
    assert "}" not in text
    assert not re.search(r"\b(TODO|FIXME|TBD|XXX)\b", text)
    assert not re.search(r"\S+@\S+", text)
    assert not re.search(r"https?://|www\.", text, re.IGNORECASE)


def test_word_count_within_limits():
    words = len(load_system_prompt().text.split())

    assert 400 <= words <= 1500
