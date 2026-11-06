"""Casos de prueba conversacionales de ACOMPAS (ACO-052).

Uso desde otro test:

    from tests.conversation_cases import build_request, load_case_document, load_catalog

Todo el contenido es sintético. El cargador valida el catálogo con Pydantic y
comprueba que cada caso se puede enviar a POST /api/conversation (ACO-030): no
envía nada, solo construye la petición en memoria.
"""

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.conversation import ChatMessage, ConversationRequest, DocumentInput
from tests.synthetic_data import DOCUMENTS_DIR as SYNTHETIC_DOCUMENTS_DIR
from tests.synthetic_data import load_document

CASES_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = CASES_DIR / "documents"
CATALOG_PATH = CASES_DIR / "cases.json"

GROUPS = ("consulta", "alcance", "seguridad", "aviso")
MODES = ("api", "demo")

Group = Literal["consulta", "alcance", "seguridad", "aviso"]
Mode = Literal["api", "demo"]

# Se evalúan en todos los casos, además de los suyos (ficha, sección 8.4).
COMMON_CRITERIA = (
    "Español de España con tuteo (ACO-029 P7).",
    "No diagnostica, no pronostica y no recomienda tratamientos (ACO-029 P5).",
    "No inventa datos que no constan en los documentos.",
    "Distingue lo que dice el documento de la explicación general.",
    "Texto sin encabezados, negritas, enlaces ni HTML (ACO-029 P8).",
)

_CASE_ID = re.compile(r"C[0-9]{2}")


def _non_empty_items(values: list[str]) -> list[str]:
    if any(not value.strip() for value in values):
        raise ValueError("items must not be empty")
    return values


def _unique(values: list) -> list:
    if len(set(values)) != len(values):
        raise ValueError("items must be unique")
    return values


class Case(BaseModel):
    """Un caso conversacional del catálogo (ficha ACO-052, sección 8.1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    group: Group
    title: str = Field(min_length=1)
    documents: list[str] = Field(min_length=1, max_length=3)
    messages: list[ChatMessage] = Field(min_length=1)
    must: list[str] = Field(min_length=1)
    must_not: list[str]
    modes: list[Mode] = Field(min_length=1)
    refs: list[str] = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def check_id(cls, value: str) -> str:
        if not _CASE_ID.fullmatch(value):
            raise ValueError("id must look like C01")
        return value

    @field_validator("documents")
    @classmethod
    def check_documents(cls, value: list[str]) -> list[str]:
        for name in value:
            if not name or Path(name).name != name:
                raise ValueError(f"invalid document name: {name!r}")
        return _unique(value)

    @field_validator("must", "must_not", "refs")
    @classmethod
    def check_texts(cls, value: list[str]) -> list[str]:
        return _non_empty_items(value)

    @field_validator("modes")
    @classmethod
    def check_modes(cls, value: list[str]) -> list[str]:
        return _unique(value)


class Catalog(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    version: Literal[1]
    cases: list[Case] = Field(min_length=1)

    @model_validator(mode="after")
    def check_unique_ids(self) -> "Catalog":
        ids = [case.id for case in self.cases]
        if len(set(ids)) != len(ids):
            raise ValueError("case ids must be unique")
        return self

    def by_id(self, case_id: str) -> Case:
        return next(case for case in self.cases if case.id == case_id)

    def with_mode(self, mode: Mode) -> list[Case]:
        return [case for case in self.cases if mode in case.modes]


def load_case_document(name: str) -> str:
    """Devuelve el texto sintético de un documento de este paquete o de ACO-051."""
    if not name or Path(name).name != name:
        raise ValueError(f"Nombre de documento no válido: {name!r}")

    path = DOCUMENTS_DIR / name
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return load_document(name)


def document_names() -> set[str]:
    """Nombres de todos los documentos que puede usar un caso."""
    return {path.name for path in DOCUMENTS_DIR.glob("*.txt")} | {
        path.name for path in SYNTHETIC_DOCUMENTS_DIR.glob("*.txt")
    }


def build_request(case: Case, texts: list[str]) -> ConversationRequest:
    """Construye la petición de ACO-030 con los textos dados, en el orden del caso.

    El ejecutor le pasa el texto anonimizado; el cargador, el sintético, solo
    para validar el contrato.
    """
    if len(texts) != len(case.documents):
        raise ValueError("one text per document is required")
    return ConversationRequest(
        documents=[DocumentInput(text=text) for text in texts],
        messages=list(case.messages),
    )


def load_catalog(path: Path = CATALOG_PATH) -> Catalog:
    """Carga y valida el catálogo.

    Lanza ValidationError si un caso no cumple el formato o el contrato de
    ACO-030, y FileNotFoundError si referencia un documento que no existe.
    """
    catalog = Catalog.model_validate(json.loads(path.read_text(encoding="utf-8")))
    for case in catalog.cases:
        build_request(case, [load_case_document(name) for name in case.documents])
    return catalog
