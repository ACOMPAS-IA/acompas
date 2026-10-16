import ast
from pathlib import Path

import app.services.llm_gateway as llm_gateway

APP_DIR = Path(__file__).resolve().parents[2] / "app"
PACKAGE_DIR = APP_DIR / "services" / "llm_gateway"
PROVIDER_MODULE = PACKAGE_DIR / "anthropic_provider.py"


def imports_anthropic(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        else:
            continue
        if any(name == "anthropic" or name.startswith("anthropic.") for name in names):
            return True
    return False


def test_only_the_provider_module_imports_anthropic():
    importers = {path for path in APP_DIR.rglob("*.py") if imports_anthropic(path)}

    assert importers == {PROVIDER_MODULE}


def test_package_files_exist():
    expected = {
        "__init__.py",
        "README.md",
        "models.py",
        "errors.py",
        "config.py",
        "provider.py",
        "anthropic_provider.py",
        "gateway.py",
    }

    assert expected <= {path.name for path in PACKAGE_DIR.iterdir()}


def test_public_contract():
    expected = {
        "LLMGateway",
        "LLMProvider",
        "LLMSettings",
        "LLMMessage",
        "LLMRequest",
        "LLMResponse",
        "LLMErrorCode",
        "LLMGatewayError",
    }

    assert set(llm_gateway.__all__) == expected
    assert len(llm_gateway.__all__) == len(expected)
    for name in expected:
        assert hasattr(llm_gateway, name)
