# 01 — PRODUCTO

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Qué es ACOMPAS: propósito, usuarios, alcance por fases, exclusiones y restricciones de producto. El agente lo usa para no salirse del producto definido al ejecutar un ACO.

## Qué no contiene

- Cómo está construido el sistema: está en 05-DISEÑO y 07-INTERCAMBIO.
- Reglas operativas: están en 03-REGLAS.
- Planificación del sprint por ACO: está en 08-PLAN.
- Equipo, costes y riesgos del Plan de Proyecto, salvo lo que restringe el producto.

## Fuentes

- **Normativas:** Plan de Proyecto (§1 Visión y principios, §2 Arquitectura técnica (resumen), §3 Equipo (actores externos), §4 Planificación y tiempos, §6 Gestión de riesgos (riesgos resueltos del mediador)).
- **Derivadas:** Casos de Uso (§1 Actores, §2 Casos de uso, §4 Planificación por sprint). Aportan detalle, pero no amplían el alcance.

## 1. Qué es ACOMPAS

ACOMPAS es una herramienta conversacional basada en inteligencia artificial. Ayuda directamente a pacientes de cáncer de páncreas, en colaboración con ACANPAN, a comprender su documentación clínica, aclarar terminología médica y preparar mejor sus consultas con el equipo oncológico. *(Plan de Proyecto §1)*

**Propósito:** es una herramienta de comprensión y traducción, no de diagnóstico. El sistema nunca sustituye al médico ni emite juicios clínicos propios. *(Plan de Proyecto §1)*

**Modelo de uso:** uso directo por pacientes, sin mediador. Hay dos roles: paciente y administrador. *(Plan de Proyecto §2 y §6, riesgos resueltos del mediador; Casos de Uso §1)*

## 2. Principios rectores de producto

*(Plan de Proyecto §1)*

- Privacidad por diseño: pseudoanonimización asistida, cifrado en reposo y en tránsito, y derecho al olvido garantizado.
- Anonimización verificable: ningún documento entra en el sistema sin pasar por la herramienta de anonimización, con validación automática por umbral de confianza.
- Persistencia útil: el historial del paciente se conserva entre sesiones.
- Entregas frecuentes: sprints de 6 semanas con demos periódicas con ACANPAN.
- Conocimiento médico actualizado: RAG con publicaciones open access de PubMed Central, con curaduría por oncólogos, a partir de la Fase 1.5.
- Simplicidad técnica: una sola base de datos.
- Seguridad por capas: incluye distinguir con claridad las respuestas basadas en una fuente recuperada de las basadas en el conocimiento interno del LLM.
- Desarrollo abierto y sin ánimo de lucro.
- **Tono cuidado (D9), pendiente de validación:** claridad, sobriedad, tranquilidad y empatía, sin falsa cercanía, dramatización, paternalismo ni lenguaje excesivamente técnico. *No está cerrado; ver Cuestiones abiertas.*

## 3. Actores

*(Casos de Uso §1; Plan de Proyecto §3)*

| Actor | Tipo | Fase | Papel |
|---|---|---|---|
| Paciente | Humano principal | Fases 1–2 | Se autentica, sube su documentación, conversa con el asistente y gestiona su historial. Usa el sistema directamente, sin mediación. |
| Administrador | Humano interno | Fases 1–2 | Gestiona usuarios, roles, configuración y lista blanca del piloto; resuelve desbloqueos de crédito. |
| Oncólogo/a | Humano externo | Fase 1.5+ | Cura el índice RAG, revisa el glosario fuera de la aplicación y evalúa la calidad clínica. |
| Claude API | Sistema externo | Fases 1–2 | LLM de la conversación sobre el documento ya anonimizado. No interviene en la anonimización. |
| Keycloak | Sistema externo | Fases 1–2 | Servidor OAuth2/OIDC: autenticación con 2FA y emisión de JWT. |
| PubMed Central | Sistema externo | Fase 1.5+ | Fuente de publicaciones open access para el RAG. |

ACANPAN participa como interlocutor institucional: valida el alcance, autoriza los emails del piloto y coordina a los pacientes participantes. *(Plan de Proyecto §3)*

## 4. Alcance funcional (casos de uso)

Inventario de los casos de uso. La columna «Fase» de los Casos de Uso es orientativa, y ante una discrepancia prevalece el Plan de Proyecto (Casos de Uso §4). La implantación técnica por sprint está en 05-DISEÑO, y el trabajo del sprint en curso, en 08-PLAN.

| Bloque | Casos de uso |
|---|---|
| Acceso | UC-01 Autenticarse (2FA) · UC-02 Gestionar usuarios y roles (incluye la lista blanca) |
| Pacientes y documentos | UC-03 Acceder (primer uso) · UC-04 Subir documento · UC-05 Anonimizar · UC-06 Validar entidades automáticamente · UC-07 Derecho al olvido · UC-20 Revisar documento anonimizado (Nivel 3) |
| Conversación | UC-08 Preguntar · UC-09 Respuesta con fuentes · UC-10 Historial · UC-11 Preguntas sugeridas · UC-12 Resumen del estado · UC-13 Guía de primeros pasos · UC-21 Ocultar o anotar un dato del resumen |
| RAG (Fase 1.5) | UC-14 Consultar RAG · UC-15 Curar fuentes · UC-16 Actualizar índice · UC-25 Validar glosario |
| Panel del paciente | UC-17 Historial y documentos · UC-18 Gestionar documentos · UC-19 Evaluar calidad (oncólogo, F2) · UC-22 Preferencias del resumen |
| Control de gasto | UC-23 Solicitar desbloqueo · UC-24 Aprobar o denegar desbloqueo |

## 5. Fases y alcance por sprint

*(Plan de Proyecto §4)*

| Fase o sprint | Objetivo | Hito |
|---|---|---|
| Fase 0 (jun–sep 2026) | Bases técnicas, legales y humanas | Acuerdo con ACANPAN e infraestructura lista |
| **S1 (sep–oct 2026)** | **Primera versión funcional: conversación con Claude sobre un informe oncológico sintético, con autenticación y anonimización básica** | **27 oct 2026: demo interna. Claude responde correctamente sobre un documento oncológico sintético** |
| S2 (oct–dic 2026) | Anonimización completa y controles obligatorios (derecho al olvido y auditoría) antes de usar datos reales; prompt refinado; trabajo preparatorio del RAG | Demo ACANPAN 1 (dic 2026), con documentos reales por primera vez; plan B: documentos ya anonimizados externamente |
| S3 (dic 2026–ene 2027) | Historial persistente (varias sesiones con título y tema), preguntas sugeridas, cita de fuente, panel básico; integración inicial del RAG | — |
| S4 (ene–mar 2027) | Motor de contexto optimizado; RAG completo | Demo ACANPAN 2 (mar 2027) |
| S5 (mar–abr 2027) | Resumen clínico exportable a PDF con preferencias editables; panel completo | — |
| S6 (abr–jul 2027) | Integración completa; pruebas con 5–10 casos reales; cierre de la anonimización | MVP (15 jul 2027) |
| Fase 1.5 (sep–dic 2027) | RAG operativo, trazabilidad y métricas de calidad | RAG operativo y oncólogo comprometido |
| Fase 2 (2028) | Validación clínica informal y financiación | — |

Parada de verano: del 15 de julio al 1 de septiembre de cada año. *(Plan de Proyecto §4)*

## 6. Exclusiones y restricciones de producto

- No diagnostica, no sustituye al médico y no emite juicios clínicos propios. *(Plan de Proyecto §1)*
- No hay rol de mediador. *(Plan de Proyecto §6; Casos de Uso §2, nota)*
- No se usa ningún dato real de paciente en ningún entorno hasta que estén operativos la anonimización, el derecho al olvido básico y el registro de auditoría. *(Plan de Proyecto §2)*
- Durante el piloto, el acceso se limita a emails autorizados por ACANPAN. *(Plan de Proyecto §2; UC-03)*
- El modelo responde solo dentro del ámbito oncológico. *(Plan de Proyecto §2)*
- Fuera del Sprint 1: ver 08-PLAN §4.

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Tono del LLM (D9): pendiente de validar con pruebas sobre casos representativos. No debe tratarse como requisito cerrado. | Plan de Proyecto §1 |
| La columna «Fase» de los casos de uso es orientativa; el sprint concreto de UC-08 (clasificador de intención) y de UC-23/24 (control de gasto) no lo fija la planificación del Plan de Proyecto. | Casos de Uso §4; Arquitectura §16 nº 1 |
| Calendario del RAG en S3–S4 (con qué corpus trabaja). | Arquitectura §16 nº 6 |
