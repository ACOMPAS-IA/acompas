# MANIFIESTO DE GENERACIÓN DEL ARNÉS

Artefacto compilado (Estrategia de Actualización Documental §4.2). Es el **único lugar** del arnés donde constan las versiones exactas de las fuentes.

## 1. Generación

| Campo | Valor |
|---|---|
| Modo | B: regeneración (anterior: modo B, 2026-10-11, commit `22004f1`) |
| Fecha | 2026-11-02 |
| Estado | **Regenerado y auditado, pendiente de revisión humana en PR**. Sin piezas detenidas. Pendientes documentales: `docs/arnes/INFORME-GENERACION.md`, sección «Regeneración (modo B) — ADR-014 y calendario del Sprint 1 (2026-11-02)» |
| Fuentes cambiadas | Plan de Trabajo (v0.10 → v0.11: §8, §9, §11, §14); Arquitectura del Sistema (v0.8 → v0.9: §16); Plan de Proyecto (v0.20 → v0.21: §4, §7, Figura 1); Documento Operativo Sprint 1 (v0.4 → v0.5: §5, §9, §14); Estrategia (v0.7 → v0.8: §6, §10); `docs/adr/` (ADR-014 y ADR-015, nuevos); fichas ACO-013, 021, 022, 027, 029 y 030, los criterios móviles de 018, 031 y 032, y el estado de revisión de 011, 012, 016 y 017. Las demás fuentes conservan versión y SHA-256 |
| Piezas regeneradas | 01, 02, 03, 05, 07, 08 y 09 |
| Piezas sin regenerar | 04-INTERFAZ: ninguna de las dos decisiones cambia la interfaz (ACO-031 fija el punto del disclaimer, pero 04 queda pendiente, PD-27); 06-SEMILLA: no cambia el corpus ni los catálogos iniciales; `AGENTS.md`: sus fuentes (Plan de Trabajo §4, §8, §9 y §10; Estrategia §4.1) no cambian de contenido |
| Instantáneas de origen | Documentos de `~/projects/acompas-fuentes/` en `f716366` (1 nov 2026); `docs/adr/` y `docs/aco/` en `a1df03b` (2 nov 2026) |
| Commit de las fuentes del repositorio | `a1df03b` (main). Entre `22004f1` y este commit se añaden ADR-014 y ADR-015, y cambian las fichas indicadas |
| Proceso | Estrategia de Actualización Documental v0.8: §4.10 y Anexo B (modo B), con las reglas del modo A |

## 2. Fuentes congeladas

| Fuente | Versión exacta | Fichero leído | SHA-256 |
|---|---|---|---|
| Plan de Proyecto | v0.21 | `ACOMPAS - Plan de Proyecto v0.21.md` | `3c8408e461bc2007a764a23b57dde65d679bbc2e307e1509a7b2cfbd906485c5` |
| Arquitectura del Sistema | v0.9 | `ACOMPAS - Arquitectura del Sistema v0.9.md` | `78010a5e09766903679b177b5a5fd36c58b9b1fa46fd09e3d9234523e5595649` |
| Plan de Trabajo | v0.11 | `ACOMPAS - Plan de Trabajo v0.11.md` | `d779d9d4dee22a70c35bc422cdbf37a089c74cc1f47fe5372e32be84b4771d02` |
| Documento Operativo Sprint 1 | v0.5 | `ACOMPAS - Documento Operativo Sprint 1 v0.5.md` | `b8858ac4534d5adde071f2688edb465bbd28c552735304d43ca91ea6574df92e` |
| Casos de Uso | v0.6 | `ACOMPAS - Casos de Uso v0.6.md` | `6558dc23bcd82e4a9ea6abaa4c7ce7b124438c56bd88a8f5e42e71976094f9e3` |
| Modelo E/R | v0.9 | `ACOMPAS - Modelo ER v0.9.md` (texto, relaciones y notas) | `724b9f94088bfd4b53995c6633653657571ebd499ba50337aac6fb44034e41d7` |
| Modelo E/R | v0.9 | `ACOMPAS - Modelo ER v0.9.docx` (solo tablas de entidades: tipo, restricción y descripción; ver nota) | `b992958748b58f09ed1f46372f31761b5f93ceec44e2ba2a353a70f7d07c8ee7` |
| Wireframes MVP | v0.5 | `ACOMPAS - Wireframes MVP v0.5.html` | `68c0216e99ecff395b2ecaf7aef6589519752014cf14609706e173319d85621b` |
| Estrategia de Actualización Documental | v0.8 | `ACOMPAS - Estrategia de Actualizacion Documental v0.8.md` (§4, incluida §4.10, y Anexos A y B) | `fc63e0684ff4c0ca03b7c91e6d130ee4922e0520789977e771bd1fbc8fa83e6f` |
| ADR aprobados | ADR-001 a ADR-015, todos «aprobado» | `docs/adr/` en el commit `a1df03b` | — |
| Fichas ACO | ACO-011 a ACO-033, ACO-051 y ACO-052 (25 fichas) | `docs/aco/` en el commit `a1df03b` (`PLANTILLA.md` no es ficha ni fuente) | — |

Ficheros de `~/projects/acompas-fuentes/`.

**Nota sobre el Modelo E/R:** al convertirse a Markdown, las tablas de entidades perdieron las columnas Tipo, Restricción y Descripción. Por autorización expresa del usuario en el PLAN, esas tablas se leyeron del .docx **de la misma versión** v0.9. El resto del .md coincide con el .docx.

**Nota sobre ADR-013:** la fuente es `docs/adr/ADR-013-politica-de-anonimizacion-y-umbral.md` del commit indicado. El fichero suelto `ADR-013.md` de `~/projects/acompas-fuentes/` no es fuente, y su texto difiere en una consecuencia.

**Nota sobre las fichas:** en `a1df03b`, las fichas de ACO-013, 022 y 030 están ampliadas y sus PR están mergeadas, pero la línea de estado de las tres sigue diciendo «pendientes de confirmar en la revisión de la PR». El arnés no lo corrige por inferencia: 08-PLAN §5 las describe con ese estado literal y el INFORME lo recoge como PD-25.

**Nota sobre ADR-015:** su contexto afirma que la demo interna del 27/10/2026 se celebró. No se celebró. El ADR está aprobado y no se edita; el arnés no compila esa premisa (INFORME, PD-26).

**Excluidas:** «ACOMPAS - Fichas ACO Sprint 1 v0.2» (la fuente de las fichas es `docs/aco/`); `ADR-013.md` suelto; contenido de ramas sin fusionar (entre otras, la ficha de ACO-022 de la PR #47); los demás .docx; el AGENTS.md y los ficheros del arnés anterior; el código; la Guía del método del arnés; el Calendario de Acciones; versiones anteriores de cualquier documento.

## 3. Condiciones previas (Estrategia §4.3)

Son las condiciones de la primera generación (modo A). En esta regeneración se han vuelto a comprobar, y su resultado no la bloquea:

| Condición | Resultado en el modo B | Evidencia |
|---|---|---|
| ADR aprobados | Cumple con salvedad | ADR-001 a ADR-015 tienen «Estado: aprobado». El registro del Plan de Trabajo v0.11 (1 nov) incluye hasta ADR-014 y aún lista ADR-015 como pendiente, porque es anterior a su aprobación (2 nov, 08:01Z). Prevalece el ADR aprobado; el desfase queda como PD-24 |
| Contradicciones conocidas cerradas | Las conocidas no detienen ninguna pieza | La cuestión 7 de la Arquitectura §16 queda cerrada por ADR-014 y retirada de la lista (Arquitectura v0.9). Siguen abiertas las discrepancias de las fuentes derivadas con ADR-013 (INFORME, PD-16 a PD-18) |
| Modelo E/R alineado con los ADR | No del todo con ADR-013 | TIPO_ETIQUETA y ETIQUETA_ANONIMIZACION siguen con `[MÉDICO_n]`, y DOCUMENTO prevé la «revisión posterior». ADR-014 no cambia el modelo de datos. Prevalecen la Arquitectura v0.9 y los ADR; queda como pendiente de la pasada B (INFORME, PD-16) |

Resultado de la primera generación:

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
| `02-DOMINIO.md` | Plan de Proyecto §1, §2; Arquitectura §1, §4, §6, §7, §8, §9; ADR-001, 002, 003, 005, 006, 007, 009, 010, 011, 012, 013, 014 | Casos de Uso §1–§3; Modelo E/R §1, §2 (tablas del .docx), §3, §4 |
| `03-REGLAS.md` | ADR-001 a 015; Arquitectura §2, §3, §4, §5, §6, §8, §9, §10, §11, §13, §14, §15; Plan de Proyecto §1, §2; Plan de Trabajo §2, §4, §5, §8, §9, §10 | Casos de Uso UC-05, UC-07, UC-09; Fichas ACO-014, 015, 021, 022, 023, 024, 025, 028, 031, 051 |
| `04-INTERFAZ.md` | Plan de Proyecto §4; Arquitectura §3, §4, §6, §7, §8, §9, §11, §14 | Casos de Uso UC-01, 03–06, 08–13, 17, 18, 20–24; Wireframes, pantallas 1–9. Lo que procede de ADR-013 se remite a 03 |
| `05-DISEÑO.md` | Arquitectura §3–§11, §13, §14; Plan de Proyecto §2; ADR-001, 003, 004, 005, 006, 007, 009, 010, 011, 012, 013, 014, 015 | Wireframes (componentes de interfaz); Modelo E/R (persistencia) |
| `06-SEMILLA.md` | Plan de Proyecto §2; Arquitectura §4, §6, §11; ADR-008, 009, 011, 013 | Fichas ACO-012, 015, 051 |
| `07-INTERCAMBIO.md` | Arquitectura §3, §4, §5, §6, §8, §9, §11, §13; ADR-001, 003, 004, 005, 006, 009, 011, 012, 013, 014, 015 | Modelo E/R §2, §3, §4; Casos de Uso UC-03, UC-07, UC-09; Fichas ACO-014, 019, 020, 021, 023, 024, 025, 027, 028, 030, 032, 051 |
| `08-PLAN.md` | Plan de Proyecto §4; Plan de Trabajo §4, §6, §9, §10, §11; Documento Operativo Sprint 1 §2, §6, §9, §10, §11, §12, §13, §14 | Fichas ACO-011 a 033, 051, 052 (objetivo, incluye, fuera de alcance, estado y criterio de revisión). Lo que procede de ADR-013, ADR-014 y ADR-015 se remite a 03 y 09 |
| `09-TESTS.md` | Plan de Proyecto §1, §2; Arquitectura §4, §11; ADR-001 a 015; Documento Operativo Sprint 1 §3, §10, §14 | Casos de Uso; Modelo E/R; Wireframes 1, 4, 5; Fichas ACO-014, 015, 019–026, 028–033, 051, 052 (criterios y tests esperados); criterios D-01…D-07 vía 08-PLAN |
| `AGENTS.md` (raíz) | Plan de Trabajo §4 (incluida «Ejecución de un ACO con un agente de IA»), §8, §9, §10; Estrategia §4.1 | — |

## 5. Cuestiones abiertas heredadas por pieza

| Cuestión abierta | Fuente | Piezas |
|---|---|---|
| Gestión de secretos en producción, rotación automática y escáner de secretos en CI | ADR-015 (Fuera de esta decisión) | 03 |
| Encaje mínimo y alcance del LLM gateway en el Sprint 1 | Plan de Trabajo §8, §9; Documento Operativo §13; ACO-027 | 03, 05, 07, 08 |
| Modelo de Claude y política de versiones | Plan de Trabajo §9 | 03, 05, 08 |
| ADR del entorno de desarrollo, sin redactar | Plan de Trabajo §9 | 08 |
| Sprint del clasificador de intención | Arquitectura §16 nº 1 | 01, 03, 05 |
| Almacenamiento de objetos | Arquitectura §16 nº 2; ADR-010 | 02, 05 |
| Diseño del derecho al olvido | Arquitectura §16 nº 3 | 03, 04, 05, 07 |
| Modelo del registro de auditoría | Arquitectura §16 nº 4 | 02, 03, 05, 07 |
| Modelo de datos definitivo | Arquitectura §16 nº 5 | 02 |
| Calendario y corpus del RAG en S3–S4 | Arquitectura §16 nº 6 | 01, 05 |
| Comprobación del tipo de documento (clínico) antes de procesarlo | Arquitectura §16 nº 8; ADR-013 | 03, 05 |
| Confianza del OCR para detectar documentos ilegibles y umbrales en los Niveles 2 y 3 o con documentos reales | Arquitectura §16 nº 9; ADR-013 | 03, 05, 09 |
| Diseño del Nivel 3 (incluida la revisión obligatoria del documento retenido cuando exista) | Arquitectura §16 nº 10; ADR-013 | 02, 03, 04, 05 |
| posicion_inicio y posicion_fin de ETIQUETA_ANONIMIZACION | Modelo E/R | 02, 07 |
| Modelo de embeddings, dimensión y chunking | ADR-007; Plan de Trabajo §9 | 02, 05 |
| «Fuera de esta decisión» de ADR-001, 003, 009, 011 y 012 | ADR correspondiente | 02, 03, 04, 06, 07 |
| «Fuera de esta decisión» de ADR-013: texto de los avisos al paciente (documento retenido e ilegible); nombre exacto de la etiqueta genérica de persona y catálogo de TIPO_ETIQUETA. Los demás puntos son las cuestiones 7 a 10 de la Arquitectura §16 y la fila de reconocedores y filtros | ADR-013 | Avisos: 03, 04, 07. Etiqueta genérica y catálogo: 02, 06, 07 |
| Formatos de entrada del Sprint 1 (texto frente a PDF o imagen) | Wireframes, pantalla 3; ACO-020; ACO-051 | 04, 07 |
| Campo «motivo» de la solicitud de desbloqueo | Wireframes, pantalla 8; Modelo E/R | 02, 04 |
| Punto de la interfaz del disclaimer | ACO-031 | 04 |
| Interfaz de la solicitud de borrado | Wireframes, pantalla 2; Arquitectura §16 nº 3 | 04 |
| Emails de prueba, catálogos iniciales y valores de crédito iniciales | ACO-015; Modelo E/R; Plan de Trabajo §9 | 06 |
| Dependencia de ACO-014 en «007», sin ficha | Documento Operativo §6 | 08 |
| Criterios pendientes en la ficha de ACO-013, 022, 030, 031 y 052 (en 013, 022 y 030 la PR ya está mergeada) | Fichas | 06, 08, 09 |
| Lista concreta de reconocedores, filtros de falsos positivos y términos permitidos (fichas de ACO-022 y ACO-023 al ampliarse) | ADR-013 (Fuera de esta decisión); ACO-022; ACO-023 | 03, 07, 08, 09 |
| Correspondencia entre las categorías del manifiesto de ACO-051 y las categorías garantizadas (T-31) | ADR-013 (Consecuencias); ACO-051 | 09 |
| Registro de auditoría del documento retenido en el Sprint 1 (T-10) | ADR-013; Arquitectura §16 nº 4 | 09 |
| Tono del LLM (D9) | Plan de Proyecto §1 | 01, 03, 09 |
| Objetivo de cobertura (más del 85%, Niveles 1–2) como métrica posterior | Arquitectura §4; ADR-003 | 03, 09 |

**Nota:** ACO-031 ya fija el punto del disclaimer en el pie permanente de `AppShell`, slot `disclaimer`. 04-INTERFAZ no se regenera en esta pasada y mantiene la cuestión abierta; queda como PD-27.

## 6. Detenciones

**Regeneración (modo B):** ninguna pieza se ha detenido. Las discrepancias entre las fuentes derivadas y ADR-013 o la Arquitectura v0.9 se resuelven por prevalencia de la fuente normativa (02-DOMINIO §5; 04-INTERFAZ §3). La cuestión 7 de la Arquitectura §16 queda cerrada por ADR-014, y la gestión de la API key por ADR-015. Detalle en `INFORME-GENERACION.md`, sección «Regeneración (modo B) — ADR-014 y calendario del Sprint 1 (2026-11-02)».

**Primera generación (modo A):**

Ninguna pieza se ha detenido. Las discrepancias detectadas se resolvieron con la prevalencia de la fuente normativa sobre la derivada (Estrategia §4.6 y §9), por decisión del usuario en el PLAN, o se recogieron como cuestión abierta. Detalle en `INFORME-GENERACION.md`.
