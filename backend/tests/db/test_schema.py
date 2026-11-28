"""Forma del esquema migrado (ACO-038: AC-02, AC-03 y AC-04).

Todo se comprueba contra la base migrada, no contra los modelos: lo que
importa es lo que PostgreSQL tiene.
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy import Inspector, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Engine

TABLAS = {
    "administrador",
    "paciente",
    "email_autorizado",
    "tipo_documento",
    "documento",
    "tipo_etiqueta",
    "etiqueta_anonimizacion",
    "sesion",
    "mensaje",
    "publicacion",
    "fragmento_rag",
    "preferencia_resumen",
    "consumo_llm",
    "credito_paciente",
    "solicitud_desbloqueo_credito",
    "entrada_glosario",
    "motivo_solicitud",
    "motivo_resolucion",
}

TABLAS_DE_OTRO_ACO = {"auditoria", "auditoria_retencion", "mensaje_fragmento"}


@pytest.fixture
def inspector(engine: Engine) -> Inspector:
    return inspect(engine)


def columnas(inspector: Inspector, tabla: str) -> dict[str, dict]:
    return {columna["name"]: columna for columna in inspector.get_columns(tabla)}


def test_tablas_del_modelo(inspector: Inspector) -> None:
    """18 tablas del modelo más la de Alembic; ninguna de auditoría."""
    tablas = set(inspector.get_table_names())
    assert tablas - {"alembic_version"} == TABLAS
    assert len(TABLAS) == 18
    assert not tablas & TABLAS_DE_OTRO_ACO


def test_claves_primarias_uuid(inspector: Inspector) -> None:
    """Todas las claves primarias son UUID (ADR-022 §1)."""
    for tabla in TABLAS:
        pk = inspector.get_pk_constraint(tabla)["constrained_columns"]
        assert pk, f"{tabla} no tiene clave primaria"
        tipos = columnas(inspector, tabla)
        for nombre in pk:
            assert isinstance(
                tipos[nombre]["type"], postgresql.UUID
            ), f"{tabla}.{nombre} no es UUID"


def test_columnas_de_la_ficha(inspector: Inspector) -> None:
    """Posiciones, hash, invalidez, embedding y array (ADR-022; ficha §8)."""
    documento = columnas(inspector, "documento")
    assert documento["hash_texto_anonimizado"]["nullable"] is False
    assert documento["hash_texto_anonimizado"]["type"].length == 64
    assert documento["hash_fichero"]["type"].length == 64
    assert documento["posiciones_validas"]["nullable"] is False

    etiqueta = columnas(inspector, "etiqueta_anonimizacion")
    assert etiqueta["posicion_inicio"]["nullable"] is False
    assert etiqueta["posicion_fin"]["nullable"] is False
    assert isinstance(etiqueta["posicion_inicio"]["type"], sa.Integer)

    fragmento = columnas(inspector, "fragmento_rag")
    assert isinstance(fragmento["embedding"]["type"], Vector)
    assert fragmento["embedding"]["type"].dim == 768
    assert fragmento["embedding"]["nullable"] is False

    mensaje = columnas(inspector, "mensaje")
    assert isinstance(mensaje["fragmentos_rag"]["type"], postgresql.ARRAY)
    assert isinstance(
        mensaje["fragmentos_rag"]["type"].item_type, postgresql.UUID
    )


def test_nombres_en_ascii(inspector: Inspector, engine: Engine) -> None:
    """Ningún identificador lleva caracteres no ASCII (ficha P10).

    El atributo que el E/R escribe con eñe se llama `anio`.
    """
    assert "anio" in columnas(inspector, "publicacion")

    nombres = _nombres(inspector, engine)
    raros = sorted(nombre for nombre in nombres if not nombre.isascii())
    assert raros == []


def test_nombres_caben_en_sesenta_y_tres(inspector: Inspector, engine: Engine) -> None:
    """Ningún identificador se trunca en PostgreSQL.

    El límite son 63 bytes; un nombre más largo se recorta en silencio y puede
    chocar con otro. La clave foránea de `motivo_resolucion` es el caso que
    obligó a quitar la tabla referida de la convención.
    """
    largos = sorted(
        (nombre for nombre in _nombres(inspector, engine) if len(nombre) > 63),
        key=len,
    )
    assert largos == []


def _nombres(inspector: Inspector, engine: Engine) -> set[str]:
    """Tablas, columnas, restricciones e índices del esquema público."""
    nombres = set(TABLAS)
    for tabla in TABLAS:
        nombres.update(columnas(inspector, tabla))
        for restriccion in (
            inspector.get_unique_constraints(tabla)
            + inspector.get_foreign_keys(tabla)
            + inspector.get_indexes(tabla)
        ):
            if restriccion.get("name"):
                nombres.add(restriccion["name"])
    with engine.connect() as connection:
        nombres.update(
            fila[0]
            for fila in connection.execute(
                sa.text(
                    "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
                )
            )
        )
        nombres.update(
            fila[0]
            for fila in connection.execute(
                sa.text(
                    "SELECT conname FROM pg_constraint "
                    "JOIN pg_class ON pg_class.oid = pg_constraint.conrelid "
                    "JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace "
                    "WHERE pg_namespace.nspname = 'public'"
                )
            )
        )
    return nombres


def test_catalogos_de_motivo(inspector: Inspector) -> None:
    """Los dos catálogos de ADR-021, con su PK y su marca de activo."""
    for tabla, pk in (
        ("motivo_solicitud", "motivo_solicitud_id"),
        ("motivo_resolucion", "motivo_resolucion_id"),
    ):
        assert inspector.get_pk_constraint(tabla)["constrained_columns"] == [pk]
        columnas_tabla = columnas(inspector, tabla)
        assert columnas_tabla["etiqueta"]["nullable"] is False
        assert columnas_tabla["activo"]["nullable"] is False


def test_restricciones_unicas(inspector: Inspector) -> None:
    """ADR-022 §5, ADR-012 y la numeración de la ficha P3."""
    esperadas = {
        "administrador": [["keycloak_id"]],
        "email_autorizado": [["email"]],
        "documento": [["paciente_id", "hash_fichero"]],
        "etiqueta_anonimizacion": [["documento_id", "tipo_etiqueta_id", "numero"]],
    }
    for tabla, columnas_unicas in esperadas.items():
        presentes = [
            restriccion["column_names"]
            for restriccion in inspector.get_unique_constraints(tabla)
        ]
        for columnas_esperadas in columnas_unicas:
            assert columnas_esperadas in presentes, f"falta el único en {tabla}"


def test_fechas_sin_zona(inspector: Inspector) -> None:
    """`TIMESTAMP` como el Modelo E/R, sin zona horaria (ficha P13)."""
    for tabla in TABLAS:
        for nombre, columna in columnas(inspector, tabla).items():
            if isinstance(columna["type"], sa.DateTime):
                assert columna["type"].timezone is False, f"{tabla}.{nombre}"


def test_indices(engine: Engine) -> None:
    """Los cinco índices del E/R §4 con su forma (AC-04)."""
    with engine.connect() as connection:
        definiciones = dict(
            connection.execute(
                sa.text(
                    "SELECT indexname, indexdef FROM pg_indexes "
                    "WHERE schemaname = 'public'"
                )
            ).all()
        )

    hnsw = definiciones["ix_fragmento_rag_embedding"]
    assert "USING hnsw" in hnsw
    assert "vector_cosine_ops" in hnsw

    assert "WHERE activa" in definiciones["ix_publicacion_activa"]
    assert "(sesion_id, creado_en)" in definiciones["ix_mensaje_sesion_id_creado_en"]

    # Los dos únicos del E/R §4 existen como índice.
    assert "uq_email_autorizado_email" in definiciones
    assert "uq_documento_paciente_id" in definiciones


def test_claves_foraneas_sin_cascada(inspector: Inspector) -> None:
    """Todas las claves foráneas son `RESTRICT` (AC-06; ficha P4)."""
    for tabla in TABLAS:
        for clave in inspector.get_foreign_keys(tabla):
            assert (
                clave["options"].get("ondelete") == "RESTRICT"
            ), f"{tabla}.{clave['constrained_columns']} no es RESTRICT"
