"""Restricciones del esquema (ACO-038: AC-03 y AC-06).

Se insertan filas sintéticas y se comprueba qué rechaza PostgreSQL. El orden de
borrado de ADR-025 §3 se apoya en que las claves foráneas sean `RESTRICT`:
aquí se verifica que un padre con hijos no se puede borrar.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest
import sqlalchemy as sa
from sqlalchemy.engine import Engine

import app.db.models  # noqa: F401  (registra las tablas en Base.metadata)
from app.db.base import Base

AHORA = datetime(2026, 11, 28, 12, 0, 0)


def tabla(nombre: str) -> sa.Table:
    return Base.metadata.tables[nombre]


def ejecutar(engine: Engine, sentencia) -> None:
    with engine.begin() as connection:
        connection.execute(sentencia)


@pytest.fixture
def paciente(engine: Engine) -> uuid.UUID:
    paciente_id = uuid.uuid4()
    ejecutar(
        engine,
        tabla("paciente")
        .insert()
        .values(paciente_id=paciente_id, creado_en=AHORA, activo=True),
    )
    return paciente_id


@pytest.fixture
def documento(engine: Engine, paciente: uuid.UUID) -> uuid.UUID:
    tipo_doc_id = uuid.uuid4()
    ejecutar(
        engine,
        tabla("tipo_documento")
        .insert()
        .values(tipo_doc_id=tipo_doc_id, nombre="Informe de patología"),
    )
    documento_id = uuid.uuid4()
    ejecutar(
        engine,
        tabla("documento")
        .insert()
        .values(
            documento_id=documento_id,
            paciente_id=paciente,
            tipo_doc_id=tipo_doc_id,
            nombre="Informe de patología 2026-11-28",
            ruta_almacen="sintetico/2026-11-28.txt",
            hash_fichero="0" * 64,
            estado_anon="validado",
            creado_en=AHORA,
            hash_texto_anonimizado="1" * 64,
        ),
    )
    return documento_id


def test_posicion_nula_se_rechaza(engine: Engine, documento: uuid.UUID) -> None:
    """Las columnas de posición son `NOT NULL` (ADR-022 §3)."""
    tipo_etiqueta_id = uuid.uuid4()
    ejecutar(
        engine,
        tabla("tipo_etiqueta")
        .insert()
        .values(tipo_etiqueta_id=tipo_etiqueta_id, etiqueta="SANITARIO"),
    )
    with pytest.raises(sa.exc.IntegrityError):
        ejecutar(
            engine,
            tabla("etiqueta_anonimizacion")
            .insert()
            .values(
                etiqueta_id=uuid.uuid4(),
                documento_id=documento,
                tipo_etiqueta_id=tipo_etiqueta_id,
                numero=1,
                tipo_entidad="PERSONAL_SANITARIO",
                fuente="presidio",
                confirmada=True,
                posicion_inicio=None,
                posicion_fin=10,
            ),
        )


def test_keycloak_id_duplicado_se_rechaza(engine: Engine) -> None:
    """`ADMINISTRADOR.keycloak_id` es único (ADR-022 §5)."""
    valores = dict(
        keycloak_id="sintetico-admin",
        nombre="Admin",
        email="admin@example.com",
        activo=True,
        creado_en=AHORA,
    )
    ejecutar(
        engine,
        tabla("administrador")
        .insert()
        .values(administrador_id=uuid.uuid4(), **valores),
    )
    with pytest.raises(sa.exc.IntegrityError):
        ejecutar(
            engine,
            tabla("administrador").insert().values(
                administrador_id=uuid.uuid4(), **valores
            ),
        )


def test_hash_repetido_por_paciente_se_rechaza(
    engine: Engine, paciente: uuid.UUID, documento: uuid.UUID
) -> None:
    """Un mismo fichero no se sube dos veces por el mismo paciente (ADR-012)."""
    with pytest.raises(sa.exc.IntegrityError):
        ejecutar(
            engine,
            tabla("documento")
            .insert()
            .values(
                documento_id=uuid.uuid4(),
                paciente_id=paciente,
                nombre="Repetido",
                ruta_almacen="sintetico/repetido.txt",
                hash_fichero="0" * 64,
                estado_anon="validado",
                creado_en=AHORA,
                hash_texto_anonimizado="2" * 64,
            ),
        )


def test_hash_repetido_en_otro_paciente_se_acepta(
    engine: Engine, documento: uuid.UUID
) -> None:
    """El único es por paciente: otro paciente puede subir el mismo fichero."""
    otro = uuid.uuid4()
    ejecutar(
        engine,
        tabla("paciente")
        .insert()
        .values(paciente_id=otro, creado_en=AHORA, activo=True),
    )
    ejecutar(
        engine,
        tabla("documento")
        .insert()
        .values(
            documento_id=uuid.uuid4(),
            paciente_id=otro,
            nombre="Mismo fichero",
            ruta_almacen="sintetico/otro.txt",
            hash_fichero="0" * 64,
            estado_anon="validado",
            creado_en=AHORA,
            hash_texto_anonimizado="3" * 64,
        ),
    )


def test_motivo_que_no_esta_en_el_catalogo_se_rechaza(
    engine: Engine, paciente: uuid.UUID
) -> None:
    """Las dos columnas de motivo son claves foráneas (ADR-021 §2)."""
    with pytest.raises(sa.exc.IntegrityError):
        ejecutar(
            engine,
            tabla("solicitud_desbloqueo_credito")
            .insert()
            .values(
                solicitud_id=uuid.uuid4(),
                paciente_id=paciente,
                fecha_solicitud=AHORA,
                motivo=uuid.uuid4(),
                estado="pendiente",
            ),
        )


def test_solicitud_pendiente_sin_motivo_se_acepta(
    engine: Engine, paciente: uuid.UUID
) -> None:
    """`motivo` es opcional y `motivo_resolucion` también (ADR-021 §1)."""
    ejecutar(
        engine,
        tabla("solicitud_desbloqueo_credito")
        .insert()
        .values(
            solicitud_id=uuid.uuid4(),
            paciente_id=paciente,
            fecha_solicitud=AHORA,
            estado="pendiente",
        ),
    )


def test_numero_de_etiqueta_repetido_se_rechaza(
    engine: Engine, documento: uuid.UUID
) -> None:
    """La numeración se reinicia por documento (ADR-012; ficha P3)."""
    tipo_etiqueta_id = uuid.uuid4()
    ejecutar(
        engine,
        tabla("tipo_etiqueta")
        .insert()
        .values(tipo_etiqueta_id=tipo_etiqueta_id, etiqueta="SANITARIO"),
    )
    valores = dict(
        documento_id=documento,
        tipo_etiqueta_id=tipo_etiqueta_id,
        numero=1,
        tipo_entidad="PERSONAL_SANITARIO",
        fuente="presidio",
        confirmada=True,
        posicion_inicio=0,
        posicion_fin=10,
    )
    ejecutar(
        engine,
        tabla("etiqueta_anonimizacion").insert().values(
            etiqueta_id=uuid.uuid4(), **valores
        ),
    )
    with pytest.raises(sa.exc.IntegrityError):
        ejecutar(
            engine,
            tabla("etiqueta_anonimizacion").insert().values(
                etiqueta_id=uuid.uuid4(), **valores
            ),
        )


def test_borrar_un_paciente_con_documentos_falla(
    engine: Engine, paciente: uuid.UUID, documento: uuid.UUID
) -> None:
    """`RESTRICT`: el orden de borrado lo lleva la aplicación (ADR-025 §3)."""
    with pytest.raises(sa.exc.IntegrityError):
        ejecutar(
            engine,
            tabla("paciente")
            .delete()
            .where(tabla("paciente").c.paciente_id == paciente),
        )


def test_borrar_una_publicacion_con_fragmentos_falla(engine: Engine) -> None:
    """El corpus no se borra por detrás de sus fragmentos."""
    publicacion_id = uuid.uuid4()
    ejecutar(
        engine,
        tabla("publicacion")
        .insert()
        .values(
            publicacion_id=publicacion_id,
            pmcid="PMC0000000",
            titulo="Artículo sintético",
            curada=True,
            activa=True,
            indexada_en=AHORA,
        ),
    )
    ejecutar(
        engine,
        tabla("fragmento_rag")
        .insert()
        .values(
            fragmento_id=uuid.uuid4(),
            publicacion_id=publicacion_id,
            contenido="Fragmento sintético",
            embedding=[0.0] * 768,
            posicion=0,
            creado_en=AHORA,
        ),
    )
    with pytest.raises(sa.exc.IntegrityError):
        ejecutar(
            engine,
            tabla("publicacion")
            .delete()
            .where(tabla("publicacion").c.publicacion_id == publicacion_id),
        )
