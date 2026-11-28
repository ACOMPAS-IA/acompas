"""Glosario construido por el LLM (ACO-038).

Entidad independiente, sin relación con el resto (E/R §2). El estado de
validación avanza con el uso; la semilla no existe y no se crea aquí.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EntradaGlosario(Base):
    """Término con su definición y su estado de validación."""

    __tablename__ = "entrada_glosario"

    termino_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    termino: Mapped[str] = mapped_column(String, nullable=False)
    definicion: Mapped[str] = mapped_column(Text, nullable=False)
    fuente: Mapped[str | None] = mapped_column(String)
    # 'pendiente', 'validada', 'corregida' o 'descartada'.
    estado_validacion: Mapped[str] = mapped_column(String, nullable=False)
    fecha_cambio_estado: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
