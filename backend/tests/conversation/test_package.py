import ast
from pathlib import Path

import app.services.conversation as conversation

APP_DIR = Path(__file__).resolve().parents[2] / "app"
PACKAGE_DIR = APP_DIR / "services" / "conversation"
API_DIR = APP_DIR / "api"

PUBLIC_API = {
    "ConversationService",
    "ConversationRequest",
    "DocumentInput",
    "ChatMessage",
    "ConversationResponse",
    "build_llm_request",
    "neutralize_delimiters",
}


def imports_anthropic(path):
    # Mismo criterio que el test de punto único de ACO-027.
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


def test_package_files_exist():
    expected = {"__init__.py", "README.md", "models.py", "messages.py", "service.py"}

    assert expected <= {path.name for path in PACKAGE_DIR.iterdir()}
    assert (API_DIR / "__init__.py").is_file()
    assert (API_DIR / "conversation.py").is_file()


def test_public_contract():
    assert set(conversation.__all__) == PUBLIC_API
    assert len(conversation.__all__) == len(PUBLIC_API)
    for name in PUBLIC_API:
        assert hasattr(conversation, name)


def test_conversation_and_router_do_not_import_anthropic():
    modules = [*PACKAGE_DIR.rglob("*.py"), *API_DIR.rglob("*.py")]

    assert modules
    assert [path for path in modules if imports_anthropic(path)] == []
