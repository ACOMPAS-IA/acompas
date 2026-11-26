"""Fixtures compartidos de las pruebas (ACO-047).

`authenticated_user` sustituye la dependencia de autenticación por un
`Principal` sintético (ACO-014). No es `autouse`: solo lo aplican con
`pytest.mark.usefixtures` los módulos que lo necesitan, para no desactivar la
autenticación en toda la suite. Los valores son sintéticos (ADR-008).
"""

import uuid

import pytest

from app.api.auth import get_current_user
from app.main import app
from app.services.auth import Principal

SYNTHETIC_PRINCIPAL = Principal(
    user_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
    email="paciente@example.com",
    roles=frozenset({"paciente"}),
)


@pytest.fixture
def authenticated_user():
    """Sustituye `get_current_user` y deja el override anterior como estaba."""
    missing = object()
    previous = app.dependency_overrides.get(get_current_user, missing)
    app.dependency_overrides[get_current_user] = lambda: SYNTHETIC_PRINCIPAL
    yield
    if previous is missing:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = previous
