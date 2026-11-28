"""Identidades: administrador, paciente y lista blanca (ACO-038).

Claves primarias UUID (ADR-022 §1). `PACIENTE.paciente_id` es el UUID de
Keycloak y no lo genera la aplicación ni se duplica en otra columna (ADR-001,
ADR-022 §6).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Administrador(Base):
    """Cuenta interna. No queda rol: solo hay un tipo de cuenta (E/R §2)."""

    __tablename__ = "administrador"

    administrador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Único y no nulo: una cuenta de Keycloak, un administrador (ADR-022 §5).
    keycloak_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Paciente(Base):
    """Paciente. El UUID lo asigna Keycloak; `activo` señala un borrado pedido."""

    __tablename__ = "paciente"

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False)


class EmailAutorizado(Base):
    """Lista blanca del piloto (ADR-009). Se retira al pasar a uso público."""

    __tablename__ = "email_autorizado"

    email_autorizado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str | None] = mapped_column(String, unique=True)
    autorizado_por: Mapped[str | None] = mapped_column(String)
    usado: Mapped[bool | None] = mapped_column(Boolean)
    creado_en: Mapped[datetime | None] = mapped_column(DateTime)
