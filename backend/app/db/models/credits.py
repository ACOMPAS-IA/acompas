"""Crédito, consumo y motivos de desbloqueo (ACO-038).

Los dos catálogos de motivo son de ADR-021: sustituyen las dos columnas `TEXT`
del E/R por claves foráneas, sin texto libre y sin `CHECK`. Nacen sin filas: la
semilla es de la ficha de UC-23/UC-24 (ADR-021 §3).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MotivoSolicitud(Base):
    """Catálogo cerrado de motivos que el paciente elige al solicitar."""

    __tablename__ = "motivo_solicitud"

    motivo_solicitud_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    etiqueta: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    # Un valor referenciado no se borra: se marca inactivo (ADR-021 §6).
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )


class MotivoResolucion(Base):
    """Catálogo cerrado de motivos de la resolución, redactados para el paciente."""

    __tablename__ = "motivo_resolucion"

    motivo_resolucion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    etiqueta: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )


class CreditoPaciente(Base):
    """Control de gasto por paciente; PK y FK a la vez (E/R §2)."""

    __tablename__ = "credito_paciente"

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paciente.paciente_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    tope_diario: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    tope_mensual: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    credito_acumulado: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    susceptible_bloqueo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    credito_infinito: Mapped[bool] = mapped_column(Boolean, nullable=False)
    modo_pruebas: Mapped[bool] = mapped_column(Boolean, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ConsumoLlm(Base):
    """Una llamada al gateway: base del control de gasto (E/R §2)."""

    __tablename__ = "consumo_llm"

    consumo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paciente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paciente.paciente_id", ondelete="RESTRICT"),
    )
    tokens_consumidos: Mapped[int] = mapped_column(Integer, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SolicitudDesbloqueoCredito(Base):
    """Solicitud de desbloqueo, con sus dos motivos como clave foránea.

    Las dos columnas admiten nulo: `motivo` es opcional y `motivo_resolucion`
    solo es obligatorio al denegar, y eso lo aplica UC-23/UC-24, no el esquema
    (ADR-021 §1).
    """

    __tablename__ = "solicitud_desbloqueo_credito"

    solicitud_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paciente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paciente.paciente_id", ondelete="RESTRICT"),
    )
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    motivo: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("motivo_solicitud.motivo_solicitud_id", ondelete="RESTRICT"),
    )
    estado: Mapped[str] = mapped_column(String, nullable=False)
    administrador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("administrador.administrador_id", ondelete="RESTRICT"),
    )
    fecha_resolucion: Mapped[datetime | None] = mapped_column(DateTime)
    motivo_resolucion: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("motivo_resolucion.motivo_resolucion_id", ondelete="RESTRICT"),
    )
