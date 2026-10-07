# MANIFIESTO DE GENERACIÓN DEL ARNÉS

Artefacto compilado (Estrategia de Actualización Documental §4.2). Es el **único lugar** del arnés donde constan las versiones exactas de las fuentes.

## 1. Generación

| Campo | Valor |
|---|---|
| Modo | A: generación completa (primera generación) |
| Fecha | 2026-10-07 |
| Estado | **Generado y auditado (2 rondas), pendiente de revisión humana en PR**. Sin piezas detenidas. Pendientes documentales: `docs/arnes/INFORME-GENERACION.md` |
| Commit de las fuentes del repositorio | `2cc2f5ac92413f88b5275e8b7964a8845a12b6d6` (main) |
| Proceso | Estrategia de Actualización Documental v0.7: §4 y Anexos A y B (modo A) |

## 2. Fuentes congeladas

| Fuente | Versión exacta | Fichero leído | SHA-256 |
|---|---|---|---|
| Plan de Proyecto | v0.20 | `ACOMPAS - Plan de Proyecto v0.20.md` | `acb7953b8b6a62f149d18aa2575177552245da5f22cf4f6bec281b65471c3229` |
| Arquitectura del Sistema | v0.7 | `ACOMPAS - Arquitectura del Sistema v0.7.md` | `2f20a818c11fcc77c71341f283a0bd062885a513b1dbfc30f8216906d4e3aaa5` |
| Plan de Trabajo | v0.9 | `ACOMPAS - Plan de Trabajo v0.9.md` | `4d0d0fc35057af970c7112d472a4d05634e5a9cf23b8f17c3c6f5579dd04ac07` |
| Documento Operativo Sprint 1 | v0.4 | `ACOMPAS - Documento Operativo Sprint 1 v0.4.md` | `d140606ea098256ffb8052471a5dbef098a114bf6b568cffc9a4621aec2cb645` |
| Casos de Uso | v0.6 | `ACOMPAS - Casos de Uso v0.6.md` | `6558dc23bcd82e4a9ea6abaa4c7ce7b124438c56bd88a8f5e42e71976094f9e3` |
| Modelo E/R | v0.9 | `ACOMPAS - Modelo ER v0.9.md` (texto, relaciones y notas) | `724b9f94088bfd4b53995c6633653657571ebd499ba50337aac6fb44034e41d7` |
| Modelo E/R | v0.9 | `ACOMPAS - Modelo ER v0.9.docx` (solo tablas de entidades: tipo, restricción y descripción; ver nota) | `b992958748b58f09ed1f46372f31761b5f93ceec44e2ba2a353a70f7d07c8ee7` |
| Wireframes MVP | v0.5 | `ACOMPAS - Wireframes MVP v0.5.html` | `68c0216e99ecff395b2ecaf7aef6589519752014cf14609706e173319d85621b` |
| Estrategia de Actualización Documental | v0.7 | `ACOMPAS - Estrategia de Actualizacion Documental v0.7.md` (§4 y Anexos A y B) | `310fdeabc8e71a4265243acabd33c050b2b23ef8d6538eaf837772e09192da00` |
| ADR aprobados | ADR-001 a ADR-012, todos «aprobado» | `docs/adr/` en el commit `2cc2f5a` | — |
| Fichas ACO | ACO-011 a ACO-033, ACO-051 y ACO-052 (25 fichas) | `docs/aco/` en el commit `2cc2f5a` (`PLANTILLA.md` no es ficha ni fuente) | — |

Ficheros de `~/projects/acompas-fuentes/`.

**Nota sobre el Modelo E/R:** al convertirse a Markdown, las tablas de entidades perdieron las columnas Tipo, Restricción y Descripción. Por autorización expresa del usuario en el PLAN, esas tablas se leyeron del .docx **de la misma versión** v0.9. El resto del .md coincide con el .docx.

**Excluidas:** «ACOMPAS - Fichas ACO Sprint 1 v0.2» (la fuente de las fichas es `docs/aco/`); los demás .docx; el AGENTS.md y los ficheros del arnés anterior; el código; la Guía del método del arnés; el Calendario de Acciones; versiones anteriores de cualquier documento.

## 3. Condiciones previas (Estrategia §4.3)

| Condición | Resultado | Evidencia |
|---|---|---|
| ADR aprobados | Cumple | Los 12 ficheros tienen «Estado: aprobado» y el registro del Plan de Trabajo §9 dice «aprobado» para ADR-001 a ADR-012 |
| Contradicciones conocidas cerradas | Cumple | Actuaciones de la pasada A aplicadas: Arquitectura v0.5/v0.6, Plan de Proyecto v0.20, Casos de Uso v0.6, Modelo E/R v0.8/v0.9 y Plan de Trabajo v0.5/v0.7 |
| Modelo E/R alineado con los ADR | Cumple | Modelo E/R v0.8 (ADR-003, 005, 010, 012) y v0.9 (posiciones abiertas) |

## 4. Piezas: fuentes y secciones

Convención: en el cuerpo de cada pieza solo se citan sus fuentes. Lo que pertenece a otra pieza se remite a ella. Las **cuestiones abiertas** citan la fuente donde la cuestión consta como abierta, aunque no sea fuente de la pieza.

| Pieza | Fuentes normativas (secciones) | Fuentes derivadas u operativas (secciones) |
|---|---|---|
| `01-PRODUCTO.md` | Plan de Proyecto §1, §2, §3, §4, §6 | Casos de Uso §1, §2, §4 |
| `02-DOMINIO.md` | Plan de Proyecto §1, §2; Arquitectura §1, §4, §6, §7, §8, §9; ADR-001, 002, 003, 005, 006, 007, 009, 010, 011, 012 | Casos de Uso §1–§3; Modelo E/R §1, §2 (tablas del .docx), §3, §4 |
| `03-REGLAS.md` | ADR-001 a 012; Arquitectura §2, §3, §4, §5, §6, §8, §9, §10, §11, §13, §14, §15; Plan de Proyecto §1, §2; Plan de Trabajo §2, §4, §5, §8, §9, §10 | Casos de Uso UC-05, UC-07, UC-09; Fichas ACO-014, 015, 021, 022, 023, 024, 025, 028, 031, 051 |
| `04-INTERFAZ.md` | Plan de Proyecto §4; Arquitectura §3, §4, §6, §7, §8, §9, §11, §14 | Casos de Uso UC-01, 03–06, 08–13, 17, 18, 20–24; Wireframes, pantallas 1–9 |
| `05-DISEÑO.md` | Arquitectura §3–§11, §13, §14; Plan de Proyecto §2; ADR-001, 003, 004, 005, 006, 007, 009, 010, 011, 012 | Wireframes (componentes de interfaz); Modelo E/R (persistencia) |
| `06-SEMILLA.md` | Plan de Proyecto §2; Arquitectura §6, §11; ADR-008, 009, 011 | Fichas ACO-012, 015, 051 |
| `07-INTERCAMBIO.md` | Arquitectura §3, §4, §5, §6, §8, §9, §11, §13; ADR-001, 003, 004, 005, 006, 009, 011, 012 | Modelo E/R §2, §3, §4; Casos de Uso UC-03, UC-07, UC-09; Fichas ACO-014, 019, 020, 021, 023, 024, 025, 027, 028, 030, 032, 051 |
| `08-PLAN.md` | Plan de Proyecto §4; Plan de Trabajo §4, §6, §10, §11; Documento Operativo Sprint 1 §2, §6, §9, §10, §11, §12, §13, §14 | Fichas ACO-011 a 033, 051, 052 (objetivo, incluye, fuera de alcance, estado y criterio de revisión) |
| `09-TESTS.md` | Plan de Proyecto §1, §2; Arquitectura §4, §11; ADR-001 a 012; Documento Operativo Sprint 1 §3, §10, §14 | Casos de Uso; Modelo E/R; Wireframes 1, 4, 5; Fichas ACO-014, 015, 019–026, 028–033, 051, 052 (criterios y tests esperados); criterios D-01…D-07 vía 08-PLAN |
| `AGENTS.md` (raíz) | Plan de Trabajo §4 (incluida «Ejecución de un ACO con un agente de IA»), §8, §9, §10; Estrategia §4.1 | — |

## 5. Cuestiones abiertas heredadas por pieza

| Cuestión abierta | Fuente | Piezas |
|---|---|---|
| Valor del umbral de confianza (los wireframes usan 0,85 como ejemplo) | Plan de Trabajo §9; ADR-003; ACO-023 | 03, 04, 08, 09 |
| Tratamiento del documento retenido por baja confianza | Plan de Trabajo §9; UC-06; Wireframes, pantalla 4; Modelo E/R (DOCUMENTO) | 02, 03, 04, 07, 09 |
| Gestión de secretos y API key de Claude (ADR pendiente) | Plan de Trabajo §9; ACO-028 | 03, 08 |
| Encaje mínimo y alcance del LLM gateway en el Sprint 1 | Plan de Trabajo §8, §9; Documento Operativo §13; ACO-027 | 03, 05, 07, 08 |
| Modelo de Claude y política de versiones | Plan de Trabajo §9 | 03, 05, 08 |
| ADR del entorno de desarrollo, sin redactar | Plan de Trabajo §9 | 08 |
| Sprint del clasificador de intención | Arquitectura §16 nº 1 | 01, 03, 05 |
| Almacenamiento de objetos | Arquitectura §16 nº 2; ADR-010 | 02, 05 |
| Diseño del derecho al olvido | Arquitectura §16 nº 3 | 03, 04, 05, 07 |
| Modelo del registro de auditoría | Arquitectura §16 nº 4 | 02, 03, 05, 07 |
| Modelo de datos definitivo | Arquitectura §16 nº 5 | 02 |
| Calendario y corpus del RAG en S3–S4 | Arquitectura §16 nº 6 | 01, 05 |
| posicion_inicio y posicion_fin de ETIQUETA_ANONIMIZACION | Modelo E/R | 02, 07 |
| Modelo de embeddings, dimensión y chunking | ADR-007; Plan de Trabajo §9 | 02, 05 |
| «Fuera de esta decisión» de ADR-001, 003, 009, 011 y 012 | ADR correspondiente | 02, 03, 04, 06, 07 |
| Formatos de entrada del Sprint 1 (texto frente a PDF o imagen) | Wireframes, pantalla 3; ACO-020; ACO-051 | 04, 07 |
| Campo «motivo» de la solicitud de desbloqueo | Wireframes, pantalla 8; Modelo E/R | 02, 04 |
| Punto de la interfaz del disclaimer | ACO-031 | 04 |
| Interfaz de la solicitud de borrado | Wireframes, pantalla 2; Arquitectura §16 nº 3 | 04 |
| Emails de prueba, catálogos iniciales y valores de crédito iniciales | ACO-015; Modelo E/R; Plan de Trabajo §9 | 06 |
| Dependencia de ACO-014 en «007», sin ficha | Documento Operativo §6 | 08 |
| Criterios pendientes de revisión de ACO-027, 029, 030, 031 y 052 | Fichas | 06, 08, 09 |
| Paso de ficha de alcance a ficha ejecutable no descrito en el Plan de Trabajo | Plan de Trabajo §4; ACO-051 | 08 |
| Identificadores del Sprint 1 (ACO-022) y filtros de falsos positivos (ACO-023) sin enumerar | ACO-022; ACO-023 | 08 |
| Tono del LLM (D9) | Plan de Proyecto §1 | 01, 03, 09 |
| Objetivo de cobertura (más del 85%, Niveles 1–2) como métrica posterior | Arquitectura §4; ADR-003 | 03, 09 |

## 6. Detenciones

Ninguna pieza se ha detenido. Las discrepancias detectadas se resolvieron con la prevalencia de la fuente normativa sobre la derivada (Estrategia §4.6 y §9), por decisión del usuario en el PLAN, o se recogieron como cuestión abierta. Detalle en `INFORME-GENERACION.md`.
