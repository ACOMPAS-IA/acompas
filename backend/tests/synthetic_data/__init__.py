"""Documentos clínicos sintéticos (ficticios) para tests y demo de ACOMPAS.

Uso desde otro test:

    from tests.synthetic_data import load_document, load_manifest
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = DATA_DIR / "documents"
MANIFEST_PATH = DATA_DIR / "expected_entities.json"


def load_document(name: str) -> str:
    """Devuelve el texto de un documento sintético por su nombre de archivo."""
    if not name or Path(name).name != name:
        raise ValueError(f"Nombre de documento no válido: {name!r}")

    path = DOCUMENTS_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"No existe el documento sintético: {name}")

    return path.read_text(encoding="utf-8")


def load_manifest() -> dict:
    """Devuelve el manifiesto de entidades esperadas."""
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def count_occurrences(text: str, document: str) -> int:
    """Cuenta las apariciones de `text` como palabra completa, sensible a mayúsculas."""
    pattern = rf"(?<!\w){re.escape(text)}(?!\w)"
    return len(re.findall(pattern, document))
