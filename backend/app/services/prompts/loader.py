"""Carga de los prompts versionados de ACOMPAS desde templates/."""

import hashlib
import re
from pathlib import Path

from .models import PromptTemplate

SYSTEM_PROMPT_VERSION = "v0"

DOCUMENT_OPEN_TAG = "<documento_clinico>"
DOCUMENT_CLOSE_TAG = "</documento_clinico>"

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_NAME_PATTERN = re.compile(r"[a-z][a-z0-9_]*")
_VERSION_PATTERN = re.compile(r"v[0-9]+")


class PromptNotFoundError(LookupError):
    """No existe una plantilla con ese nombre y esa versión."""


def load_prompt(name: str, version: str) -> PromptTemplate:
    """Lee templates/{name}_{version}.md y lo devuelve con su huella."""
    # fullmatch: con match, "$" aceptaría un salto de línea final.
    if not isinstance(name, str) or not _NAME_PATTERN.fullmatch(name):
        raise ValueError(f"invalid prompt name: {name!r}")
    if not isinstance(version, str) or not _VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"invalid prompt version: {version!r}")

    path = _TEMPLATES_DIR / f"{name}_{version}.md"
    if not path.is_file():
        raise PromptNotFoundError(f"prompt not found: {name}_{version}")

    text = path.read_text(encoding="utf-8").strip()
    return PromptTemplate(
        name=name,
        version=version,
        text=text,
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def load_system_prompt() -> PromptTemplate:
    """Devuelve el system prompt que usa la aplicación."""
    return load_prompt("system", SYSTEM_PROMPT_VERSION)
