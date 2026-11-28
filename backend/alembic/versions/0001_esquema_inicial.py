"""Esquema inicial: las 18 tablas del Sprint 2

Revision ID: 0001
Revises:
Create Date: 2026-11-28

Las diecisiete entidades del Modelo E/R §2 menos `AUDITORIA` —que llega con
ACO-039 y su propia migración (ADR-024 §7)— más `MOTIVO_SOLICITUD` y
`MOTIVO_RESOLUCION` (ADR-021 §2).

Forma de las tablas: ADR-022 (UUID, posiciones `NOT NULL`, hash del texto
canónico, `keycloak_id` único) y ADR-021 (dos catálogos y sus claves foráneas).
Las decisiones de la ficha que ninguna fuente fija están en su sección 0.

La extensión `vector` se crea aquí porque el servicio de la CI no ejecuta
`infra/docker/postgres/init`. No se elimina en `downgrade`: es compartida y
puede haber sido creada antes que esta migración.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "administrador",
        sa.Column("administrador_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("keycloak_id", sa.String(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("administrador_id", name="pk_administrador"),
        sa.UniqueConstraint("keycloak_id", name="uq_administrador_keycloak_id"),
    )

    op.create_table(
        "paciente",
        # El UUID lo asigna Keycloak (ADR-001, ADR-022 §6).
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("paciente_id", name="pk_paciente"),
    )

    op.create_table(
        "email_autorizado",
        sa.Column(
            "email_autorizado_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("autorizado_por", sa.String(), nullable=True),
        sa.Column("usado", sa.Boolean(), nullable=True),
        sa.Column("creado_en", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("email_autorizado_id", name="pk_email_autorizado"),
        sa.UniqueConstraint("email", name="uq_email_autorizado_email"),
    )

    op.create_table(
        "tipo_documento",
        sa.Column("tipo_doc_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("tipo_doc_id", name="pk_tipo_documento"),
    )

    op.create_table(
        "tipo_etiqueta",
        sa.Column("tipo_etiqueta_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("etiqueta", sa.String(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("tipo_etiqueta_id", name="pk_tipo_etiqueta"),
    )

    op.create_table(
        "motivo_solicitud",
        sa.Column(
            "motivo_solicitud_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("etiqueta", sa.String(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column(
            "activo", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.PrimaryKeyConstraint("motivo_solicitud_id", name="pk_motivo_solicitud"),
    )

    op.create_table(
        "motivo_resolucion",
        sa.Column(
            "motivo_resolucion_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("etiqueta", sa.String(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column(
            "activo", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.PrimaryKeyConstraint("motivo_resolucion_id", name="pk_motivo_resolucion"),
    )

    op.create_table(
        "documento",
        sa.Column("documento_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tipo_doc_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("ruta_almacen", sa.String(), nullable=False),
        # SHA-256 del fichero original, hexadecimal minúsculas (ficha P12).
        sa.Column("hash_fichero", sa.String(length=64), nullable=False),
        sa.Column("estado_anon", sa.String(), nullable=False),
        sa.Column("confianza_automatica", sa.Numeric(), nullable=True),
        sa.Column("validado_en", sa.DateTime(), nullable=True),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        # SHA-256 del texto canónico del anonimizado (ADR-022 §4; ficha P1).
        sa.Column("hash_texto_anonimizado", sa.String(length=64), nullable=False),
        # La invalidez es del documento (ADR-022 §4; ficha P2).
        sa.Column(
            "posiciones_validas",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["paciente.paciente_id"],
            name="fk_documento_paciente_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tipo_doc_id"],
            ["tipo_documento.tipo_doc_id"],
            name="fk_documento_tipo_doc_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("documento_id", name="pk_documento"),
        sa.UniqueConstraint(
            "paciente_id", "hash_fichero", name="uq_documento_paciente_id"
        ),
    )

    op.create_table(
        "etiqueta_anonimizacion",
        sa.Column("etiqueta_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("documento_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tipo_etiqueta_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("tipo_entidad", sa.String(), nullable=False),
        sa.Column("fuente", sa.String(), nullable=False),
        sa.Column("confirmada", sa.Boolean(), nullable=False),
        # Intervalo [inicio, fin), base 0, en puntos de código sobre el texto
        # canónico (ADR-022 §2 y §3).
        sa.Column("posicion_inicio", sa.Integer(), nullable=False),
        sa.Column("posicion_fin", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["documento_id"],
            ["documento.documento_id"],
            name="fk_etiqueta_anonimizacion_documento_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tipo_etiqueta_id"],
            ["tipo_etiqueta.tipo_etiqueta_id"],
            name="fk_etiqueta_anonimizacion_tipo_etiqueta_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("etiqueta_id", name="pk_etiqueta_anonimizacion"),
        sa.UniqueConstraint(
            "documento_id",
            "tipo_etiqueta_id",
            "numero",
            name="uq_etiqueta_anonimizacion_documento_id",
        ),
    )

    op.create_table(
        "sesion",
        sa.Column("sesion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("titulo", sa.String(), nullable=True),
        sa.Column("tema", sa.String(), nullable=True),
        sa.Column("iniciada_en", sa.DateTime(), nullable=False),
        sa.Column("ultima_actividad", sa.DateTime(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["paciente.paciente_id"],
            name="fk_sesion_paciente_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("sesion_id", name="pk_sesion"),
    )

    op.create_table(
        "mensaje",
        sa.Column("mensaje_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sesion_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rol", sa.String(), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("tokens_usados", sa.Integer(), nullable=True),
        # Array de `fragmento_rag.fragmento_id`, sin tabla de unión (ficha P8).
        sa.Column(
            "fragmentos_rag",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sesion_id"],
            ["sesion.sesion_id"],
            name="fk_mensaje_sesion_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("mensaje_id", name="pk_mensaje"),
    )
    op.create_index(
        "ix_mensaje_sesion_id_creado_en",
        "mensaje",
        ["sesion_id", "creado_en"],
        unique=False,
    )

    op.create_table(
        "publicacion",
        sa.Column("publicacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pmcid", sa.String(), nullable=False),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("autores", sa.Text(), nullable=True),
        # El E/R lo escribe con eñe; el nombre físico es ASCII (ficha P10).
        sa.Column("anio", sa.Integer(), nullable=True),
        sa.Column("doi", sa.String(), nullable=True),
        sa.Column("tipo_evidencia", sa.String(), nullable=True),
        sa.Column("curada", sa.Boolean(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("indexada_en", sa.DateTime(), nullable=False),
        sa.Column("invalidada_en", sa.DateTime(), nullable=True),
        sa.Column("motivo_invalidacion", sa.Text(), nullable=True),
        sa.Column("referencia_curaduria", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("publicacion_id", name="pk_publicacion"),
    )
    op.create_index(
        "ix_publicacion_activa",
        "publicacion",
        ["activa"],
        unique=False,
        postgresql_where=sa.text("activa"),
    )

    op.create_table(
        "fragmento_rag",
        sa.Column("fragmento_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("publicacion_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contenido", sa.Text(), nullable=False),
        # Dimensión del Modelo E/R §2, provisional (Arquitectura §16 nº 14;
        # ficha P9).
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column("posicion", sa.Integer(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["publicacion_id"],
            ["publicacion.publicacion_id"],
            name="fk_fragmento_rag_publicacion_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("fragmento_id", name="pk_fragmento_rag"),
    )
    op.create_index(
        "ix_fragmento_rag_embedding",
        "fragmento_rag",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    op.create_table(
        "preferencia_resumen",
        sa.Column("preferencia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("campo_o_seccion", sa.String(), nullable=False),
        sa.Column("texto", sa.Text(), nullable=True),
        sa.Column(
            "alcance",
            sa.String(),
            nullable=False,
            server_default=sa.text("'siempre'"),
        ),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["paciente.paciente_id"],
            name="fk_preferencia_resumen_paciente_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("preferencia_id", name="pk_preferencia_resumen"),
    )

    op.create_table(
        "consumo_llm",
        sa.Column("consumo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tokens_consumidos", sa.Integer(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["paciente.paciente_id"],
            name="fk_consumo_llm_paciente_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("consumo_id", name="pk_consumo_llm"),
    )

    op.create_table(
        "credito_paciente",
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tope_diario", sa.Numeric(), nullable=False),
        sa.Column("tope_mensual", sa.Numeric(), nullable=False),
        sa.Column("credito_acumulado", sa.Numeric(), nullable=False),
        sa.Column("susceptible_bloqueo", sa.Boolean(), nullable=False),
        sa.Column("credito_infinito", sa.Boolean(), nullable=False),
        sa.Column("modo_pruebas", sa.Boolean(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["paciente.paciente_id"],
            name="fk_credito_paciente_paciente_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("paciente_id", name="pk_credito_paciente"),
    )

    op.create_table(
        "solicitud_desbloqueo_credito",
        sa.Column("solicitud_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("fecha_solicitud", sa.DateTime(), nullable=False),
        # Las dos columnas admiten nulo: la obligatoriedad al denegar es de
        # UC-23/UC-24 (ADR-021 §1).
        sa.Column("motivo", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("estado", sa.String(), nullable=False),
        sa.Column("administrador_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("fecha_resolucion", sa.DateTime(), nullable=True),
        sa.Column("motivo_resolucion", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["paciente.paciente_id"],
            name="fk_solicitud_desbloqueo_credito_paciente_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["motivo"],
            ["motivo_solicitud.motivo_solicitud_id"],
            name="fk_solicitud_desbloqueo_credito_motivo",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["administrador_id"],
            ["administrador.administrador_id"],
            name="fk_solicitud_desbloqueo_credito_administrador_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["motivo_resolucion"],
            ["motivo_resolucion.motivo_resolucion_id"],
            name="fk_solicitud_desbloqueo_credito_motivo_resolucion",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("solicitud_id", name="pk_solicitud_desbloqueo_credito"),
    )

    op.create_table(
        "entrada_glosario",
        sa.Column("termino_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("termino", sa.String(), nullable=False),
        sa.Column("definicion", sa.Text(), nullable=False),
        sa.Column("fuente", sa.String(), nullable=True),
        sa.Column("estado_validacion", sa.String(), nullable=False),
        sa.Column("fecha_cambio_estado", sa.DateTime(), nullable=True),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("termino_id", name="pk_entrada_glosario"),
    )


def downgrade() -> None:
    op.drop_table("entrada_glosario")
    op.drop_table("solicitud_desbloqueo_credito")
    op.drop_table("credito_paciente")
    op.drop_table("consumo_llm")
    op.drop_table("preferencia_resumen")
    op.drop_index("ix_fragmento_rag_embedding", table_name="fragmento_rag")
    op.drop_table("fragmento_rag")
    op.drop_index("ix_publicacion_activa", table_name="publicacion")
    op.drop_table("publicacion")
    op.drop_index("ix_mensaje_sesion_id_creado_en", table_name="mensaje")
    op.drop_table("mensaje")
    op.drop_table("sesion")
    op.drop_table("etiqueta_anonimizacion")
    op.drop_table("documento")
    op.drop_table("motivo_resolucion")
    op.drop_table("motivo_solicitud")
    op.drop_table("tipo_etiqueta")
    op.drop_table("tipo_documento")
    op.drop_table("email_autorizado")
    op.drop_table("paciente")
    op.drop_table("administrador")
    # La extensión `vector` se queda: es compartida y puede ser anterior.
