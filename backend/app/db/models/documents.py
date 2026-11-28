"""Documentos y etiquetas de anonimización (ACO-038).

Aquí están las dos decisiones de ADR-022 que cambian el E/R: el hash del texto
canónico en `DOCUMENTO` (§4) y las dos columnas de posición `NOT NULL` (§3).
El anclaje es al texto anonimizado, nunca al original (ADR-005, ADR-012).
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
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TipoDocumento(Base):
    """Catálogo de tipos de documento. Nace sin filas (ficha §5)."""

    __tablename__ = "tipo_documento"

    tipo_doc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)


class Documento(Base):
    """Documento anonimizado. El original no se persiste (ADR-005)."""

    __tablename__ = "documento"
    __table_args__ = (
        # Un mismo fichero no se sube dos veces por el mismo paciente
        # (ADR-012).
        UniqueConstraint("paciente_id", "hash_fichero"),
    )

    documento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paciente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paciente.paciente_id", ondelete="RESTRICT"),
    )
    tipo_doc_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tipo_documento.tipo_doc_id", ondelete="RESTRICT"),
    )
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    ruta_almacen: Mapped[str] = mapped_column(String, nullable=False)
    # SHA-256 del fichero original, en hexadecimal minúsculas (ficha P12).
    hash_fichero: Mapped[str] = mapped_column(String(64), nullable=False)
    estado_anon: Mapped[str] = mapped_column(String, nullable=False)
    confianza_automatica: Mapped[Decimal | None] = mapped_column(Numeric)
    validado_en: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # SHA-256 del texto canónico del anonimizado, hexadecimal minúsculas. Es el
    # control de integridad de las posiciones y no sustituye a `hash_fichero`
    # (ADR-022 §4; ficha P1).
    hash_texto_anonimizado: Mapped[str] = mapped_column(String(64), nullable=False)
    # La invalidez es del documento y las posiciones siguen NOT NULL
    # (ADR-022 §4; ficha P2).
    posiciones_validas: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )


class TipoEtiqueta(Base):
    """Catálogo de tipos de etiqueta, sin numeración (ADR-012)."""

    __tablename__ = "tipo_etiqueta"

    tipo_etiqueta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    etiqueta: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)


class EtiquetaAnonimizacion(Base):
    """Etiqueta de un documento, anclada a su texto canónico.

    `posicion_inicio` y `posicion_fin` son el intervalo semiabierto
    `[inicio, fin)`, base 0, en puntos de código sobre el texto que guarda
    `DOCUMENTO.ruta_almacen` (ADR-022 §2 y §3). No se guarda el valor original
    de ninguna entidad (ADR-012).
    """

    __tablename__ = "etiqueta_anonimizacion"
    __table_args__ = (
        # `numero` reinicia en cada documento y lo localiza junto al tipo
        # (ADR-012; ficha P3).
        UniqueConstraint("documento_id", "tipo_etiqueta_id", "numero"),
    )

    etiqueta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    documento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documento.documento_id", ondelete="RESTRICT"),
    )
    tipo_etiqueta_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tipo_etiqueta.tipo_etiqueta_id", ondelete="RESTRICT"),
    )
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_entidad: Mapped[str] = mapped_column(String, nullable=False)
    # 'presidio' o 'paciente' (ADR-003).
    fuente: Mapped[str] = mapped_column(String, nullable=False)
    confirmada: Mapped[bool] = mapped_column(Boolean, nullable=False)
    posicion_inicio: Mapped[int] = mapped_column(Integer, nullable=False)
    posicion_fin: Mapped[int] = mapped_column(Integer, nullable=False)
