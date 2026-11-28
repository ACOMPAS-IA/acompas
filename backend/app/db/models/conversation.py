"""Conversación y corpus documental (ACO-038).

`MENSAJE.fragmentos_rag` es un array de UUID, como el Modelo E/R §2: no hay
tabla de unión. ADR-025 §2 la nombra, y la incoherencia queda registrada en
`docs/seguimientos.md` (ficha P8).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Sesion(Base):
    """Conversación temática de un paciente (E/R §2)."""

    __tablename__ = "sesion"

    sesion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paciente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paciente.paciente_id", ondelete="RESTRICT"),
    )
    titulo: Mapped[str | None] = mapped_column(String)
    tema: Mapped[str | None] = mapped_column(String)
    iniciada_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ultima_actividad: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Mensaje(Base):
    """Mensaje de una sesión, con los fragmentos RAG que lo sustentan."""

    __tablename__ = "mensaje"
    __table_args__ = (
        # Historial de una sesión en orden (E/R §4).
        Index("ix_mensaje_sesion_id_creado_en", "sesion_id", "creado_en"),
    )

    mensaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sesion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sesion.sesion_id", ondelete="RESTRICT"),
    )
    rol: Mapped[str] = mapped_column(String, nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_usados: Mapped[int | None] = mapped_column(Integer)
    # Array de `fragmento_rag.fragmento_id`: sin integridad referencial, porque
    # el E/R no declara tabla de unión (ficha P8).
    fragmentos_rag: Mapped[list[uuid.UUID] | None] = mapped_column(
        ARRAY(UUID(as_uuid=True))
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Publicacion(Base):
    """Publicación del corpus, con su ciclo de vida en el índice RAG."""

    __tablename__ = "publicacion"
    __table_args__ = (
        # El pipeline RAG filtra por publicaciones vigentes (E/R §4).
        Index("ix_publicacion_activa", "activa", postgresql_where=text("activa")),
    )

    publicacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pmcid: Mapped[str] = mapped_column(String, nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    autores: Mapped[str | None] = mapped_column(Text)
    # El E/R lo escribe con eñe; el nombre físico es ASCII (ficha P10).
    anio: Mapped[int | None] = mapped_column(Integer)
    doi: Mapped[str | None] = mapped_column(String)
    tipo_evidencia: Mapped[str | None] = mapped_column(String)
    curada: Mapped[bool] = mapped_column(Boolean, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False)
    indexada_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    invalidada_en: Mapped[datetime | None] = mapped_column(DateTime)
    motivo_invalidacion: Mapped[str | None] = mapped_column(Text)
    referencia_curaduria: Mapped[str | None] = mapped_column(String)


class FragmentoRag(Base):
    """Trozo de una publicación con su embedding.

    La dimensión 768 es la del Modelo E/R §2 y sigue provisional hasta decidir
    el modelo de embeddings (Arquitectura §16 nº 14; ficha P9). Cambiarla
    exige migración y reindexado.
    """

    __tablename__ = "fragmento_rag"
    __table_args__ = (
        Index(
            "ix_fragmento_rag_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    fragmento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publicacion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publicacion.publicacion_id", ondelete="RESTRICT"),
    )
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)
    posicion: Mapped[int] = mapped_column(Integer, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
