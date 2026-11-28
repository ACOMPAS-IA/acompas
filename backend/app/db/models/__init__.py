"""Modelo de datos del Sprint 2 (ACO-038).

Importar este paquete registra las 18 tablas en `Base.metadata`. Lo hace
Alembic (`alembic/env.py`) y lo hacen los tests; la aplicación no lo necesita
hasta ACO-043.

Diecisiete entidades del Modelo E/R §2 menos `AUDITORIA` —que es de ACO-039,
con su propia migración (ADR-024 §7)— más `MOTIVO_SOLICITUD` y
`MOTIVO_RESOLUCION` (ADR-021 §2).
"""

from __future__ import annotations

from app.db.base import Base
from app.db.models.accounts import Administrador, EmailAutorizado, Paciente
from app.db.models.conversation import (
    FragmentoRag,
    Mensaje,
    Publicacion,
    Sesion,
)
from app.db.models.credits import (
    ConsumoLlm,
    CreditoPaciente,
    MotivoResolucion,
    MotivoSolicitud,
    SolicitudDesbloqueoCredito,
)
from app.db.models.documents import (
    Documento,
    EtiquetaAnonimizacion,
    TipoDocumento,
    TipoEtiqueta,
)
from app.db.models.glossary import EntradaGlosario
from app.db.models.preferences import PreferenciaResumen

__all__ = [
    "Administrador",
    "Base",
    "ConsumoLlm",
    "CreditoPaciente",
    "Documento",
    "EmailAutorizado",
    "EntradaGlosario",
    "EtiquetaAnonimizacion",
    "FragmentoRag",
    "Mensaje",
    "MotivoResolucion",
    "MotivoSolicitud",
    "Paciente",
    "PreferenciaResumen",
    "Publicacion",
    "Sesion",
    "SolicitudDesbloqueoCredito",
    "TipoDocumento",
    "TipoEtiqueta",
]
