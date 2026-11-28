"""Preferencias sobre el resumen clínico (ACO-038).

Entidad derivada de la Arquitectura; no se relaciona con el texto de cada
resumen, solo con el paciente (E/R §2). `alcance` nace con `'siempre'`.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PreferenciaResumen(Base):
    """Ocultar o anotar un campo o sección del resumen exportable."""

    __tablename__ = "preferencia_resumen"

    preferencia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paciente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paciente.paciente_id", ondelete="RESTRICT"),
    )
    # 'ocultar' o 'anotar'.
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    campo_o_seccion: Mapped[str] = mapped_column(String, nullable=False)
    texto: Mapped[str | None] = mapped_column(Text)
    # Ámbito de aplicación; el E/R fija 'siempre' como valor por defecto.
    alcance: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'siempre'")
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
