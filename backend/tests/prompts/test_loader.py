import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

import app.services.prompts as prompts
from app.services.prompts import (
    DOCUMENT_CLOSE_TAG,
    DOCUMENT_OPEN_TAG,
    SYSTEM_PROMPT_VERSION,
    PromptNotFoundError,
    PromptTemplate,
    load_prompt,
    load_system_prompt,
)

PUBLIC_API = {
    "PromptTemplate",
    "PromptNotFoundError",
    "load_prompt",
    "load_system_prompt",
    "SYSTEM_PROMPT_VERSION",
    "DOCUMENT_OPEN_TAG",
    "DOCUMENT_CLOSE_TAG",
}

PACKAGE_DIR = Path(prompts.__file__).resolve().parent
TESTS_DIR = Path(__file__).resolve().parent


def test_load_system_prompt_returns_v0():
    prompt = load_system_prompt()

    assert isinstance(prompt, PromptTemplate)
    assert prompt.name == "system"
    assert prompt.version == "v0"
    assert prompt.text
    assert prompt.text == prompt.text.strip()
    assert prompt.sha256 == hashlib.sha256(prompt.text.encode("utf-8")).hexdigest()


def test_load_prompt_matches_load_system_prompt():
    assert load_prompt("system", "v0") == load_system_prompt()


@pytest.mark.parametrize(
    ("name", "version"),
    [("system", "v99"), ("inexistente", "v0")],
)
def test_load_prompt_missing_template_raises_not_found(name, version):
    with pytest.raises(PromptNotFoundError):
        load_prompt(name, version)

    assert issubclass(PromptNotFoundError, LookupError)


@pytest.mark.parametrize(
    ("name", "version"),
    [
        ("", "v0"),
        ("System", "v0"),
        ("1system", "v0"),
        ("../system", "v0"),
        ("system/../x", "v0"),
        ("/etc/passwd", "v0"),
        ("sys.tem", "v0"),
        ("system\n", "v0"),
        (None, "v0"),
        ("system", ""),
        ("system", "0"),
        ("system", "V0"),
        ("system", "v"),
        ("system", "v0/../.."),
        ("system", "v0\n"),
        ("system", "v0.md"),
        ("system", 0),
    ],
)
def test_load_prompt_rejects_invalid_name_or_version(monkeypatch, name, version):
    def fail(*args, **kwargs):
        raise AssertionError("the loader must not access the disk")

    monkeypatch.setattr(Path, "is_file", fail)
    monkeypatch.setattr(Path, "read_text", fail)

    with pytest.raises(ValueError):
        load_prompt(name, version)


def test_prompt_template_is_immutable():
    prompt = load_system_prompt()

    with pytest.raises(ValidationError):
        prompt.text = "otro texto"


def test_public_api_exports_exactly_contract():
    assert set(prompts.__all__) == PUBLIC_API
    assert len(prompts.__all__) == len(PUBLIC_API)
    for name in PUBLIC_API:
        assert hasattr(prompts, name)

    assert SYSTEM_PROMPT_VERSION == "v0"
    assert DOCUMENT_OPEN_TAG == "<documento_clinico>"
    assert DOCUMENT_CLOSE_TAG == "</documento_clinico>"


def test_package_files_exist():
    for relative in [
        "__init__.py",
        "README.md",
        "models.py",
        "loader.py",
        "templates/system_v0.md",
    ]:
        assert (PACKAGE_DIR / relative).is_file(), relative

    for relative in ["__init__.py", "test_loader.py", "test_system_prompt.py"]:
        assert (TESTS_DIR / relative).is_file(), relative
