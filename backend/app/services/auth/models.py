"""Identidad autenticada que se obtiene del JWT (ACO-014, sección 8.4)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Principal(BaseModel):
    """Usuario autenticado.

    El email llega en el token y no se persiste: la correspondencia
    email↔UUID es de Keycloak (ADR-001).
    """

    model_config = ConfigDict(frozen=True)

    user_id: UUID
    email: str | None = None
    roles: frozenset[str] = Field(default_factory=frozenset)
