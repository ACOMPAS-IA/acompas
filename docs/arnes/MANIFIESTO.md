# MANIFIESTO DE GENERACIÓN DEL ARNÉS

Artefacto compilado (Estrategia de Actualización Documental §4.2). Es el **único lugar** del arnés donde constan las versiones exactas de las fuentes.

## 1. Generación

| Campo | Valor |
|---|---|
| Modo | B: regeneración (anterior: modo B, 2026-11-02, commit `0a2d6f0`) |
| Fecha | 2026-11-13 |
| Estado | **Regenerado y auditado, pendiente de revisión humana en PR**. Sin piezas detenidas. Pendientes documentales: `docs/arnes/INFORME-GENERACION.md`, sección «Regeneración (modo B) — pasada B (2026-11-13)» |
| Fuentes cambiadas | Plan de Proyecto (v0.21 → v0.22: §1, §6, §7); Arquitectura del Sistema (v0.9 → v0.10: §16); Plan de Trabajo (v0.11 → v0.12: §8, §9, §11, §12, §13); Documento Operativo Sprint 1 (v0.5 → v0.7: §6, §9, §10, §14, §16); Casos de Uso (v0.6 → v0.7: §2, §3, portada); Modelo E/R (v0.9 → v0.10: §1, §2); Wireframes MVP (v0.5 → v0.6: pantallas 2–5, 8, 9, nuevas 4b, 4c y 10); `docs/adr/` (ADR-016, ADR-017 y ADR-018, nuevos); 18 fichas ACO (ACO-012, 014, 015, 018, 019, 020, 021, 023, 024, 025, 026, 027, 028, 030, 031, 032, 033 y 052). La Estrategia v0.8 y las demás fuentes conservan versión (su SHA-256 es el de `85c0ab4`; el de la instantánea vigente `f7eff22` consta en §2, con las notas de forma). Después, en `4275ef0`, cambia la línea de estado de ocho fichas (PD-25) |
| Piezas regeneradas | 01, 02, 03, 04, 05, 06, 07, 08 y 09 |
| Piezas sin regenerar | `AGENTS.md`: sus fuentes (Plan de Trabajo §4, §8, §9 y §10; Estrategia §4.1) no cambian de contenido |
| Instantáneas de origen | Documentos de `~/projects/acompas-fuentes/` en `90acd3c` (13 nov 2026), publicados en `main` de `acompas-fuentes` en `85c0ab4`; la instantánea vigente de las fuentes es `f7eff22` (14 nov 2026), con `sha256sum -c SHA256SUMS`: 17/17. Entre `85c0ab4` y `f7eff22` solo hay cambios de forma (notas del §2); `docs/adr/` en `7cc69b9` y `docs/aco/` en `4275ef0` (rama `docs/pasada-b-fichas`) |
| Commit de las fuentes del repositorio | `7cc69b9` para `docs/adr/` y `4275ef0` para `docs/aco/` (rama `docs/pasada-b-fichas`). Entre `a1df03b` y `7cc69b9` se añaden ADR-016, ADR-017 y ADR-018; en `4275ef0` se corrigen las líneas de estado de ocho fichas (PD-25) |
| Proceso | Estrategia de Actualización Documental v0.8: §4.10 y Anexo B (modo B), con las reglas del modo A |

## 2. Fuentes congeladas

| Fuente | Versión exacta | Fichero leído | SHA-256 |
|---|---|---|---|
| Plan de Proyecto | v0.22 | `ACOMPAS - Plan de Proyecto v0.22.md` | `3d7fc2070c9686b5e9ad2805afe7f095d6be37d63ca7c7863ac0536ea41701c4` |
| Arquitectura del Sistema | v0.10 | `ACOMPAS - Arquitectura del Sistema v0.10.md` | `b8c47bdffb2654473c5380622232cefdce8b57dcd812dc479299f1b644a005c2` |
| Plan de Trabajo | v0.12 | `ACOMPAS - Plan de Trabajo v0.12.md` | `e55e139088890dfe282f0562f433bb3c0aae668294098f7c692012c97b9e10ea` |
| Documento Operativo Sprint 1 | v0.7 | `ACOMPAS - Documento Operativo Sprint 1 v0.7.md` | `279d34241d3158a859d36ea7f32303443070504124980aa6d2933e965613a409` |
| Casos de Uso | v0.7 | `ACOMPAS - Casos de Uso v0.7.md` | `9b43a423dfdddd5c8dcb3f87b14a1474b1cbc2da40a86b576ee5f1306c09e1f7` |
| Modelo E/R | v0.10 | `ACOMPAS - Modelo ER v0.10.md` (ver nota) | `11110481b8c6332e759419319adcb29600762d17bfc552437d84eb058c724013` |
| Wireframes MVP | v0.6 | `ACOMPAS - Wireframes MVP v0.6.html` | `b4d63f90de233b7353da077f084a0778ee0d2b877234518cf46ecdc27fc72912` |
| Estrategia de Actualización Documental | v0.8 | `ACOMPAS - Estrategia de Actualizacion Documental v0.8.md` (§4, incluida §4.10, y Anexos A y B) | `f509a3c187b67d5d25f7c0cc4cf39032f3e6d3f038e4956369af5e02d13f8a26` |
| ADR aprobados | ADR-001 a ADR-018, todos «aprobado» | `docs/adr/` en el commit `7cc69b9` | — |
| Fichas ACO | ACO-011 a ACO-033, ACO-051 y ACO-052 (25 fichas) | `docs/aco/` en el commit `4275ef0` (`PLANTILLA.md` no es ficha ni fuente) | — |

Ficheros de `~/projects/acompas-fuentes/`.

**Nota sobre el Modelo E/R:** en la instantánea `90acd3c`, al convertirse a Markdown, las tablas de entidades perdieron las columnas Tipo, Restricción y Descripción, y por autorización expresa del usuario en el PLAN se leyeron del .docx **de la misma versión**. Corregido en `ACOMPAS-IA/acompas-fuentes#4` (PD-04): el `.md` de `f7eff22` conserva las cuatro columnas y es la única fuente que se cita. El contenido compilado en las piezas es el mismo.

**Nota sobre la exportación:** los `.md` de `f7eff22` se exportan todos con `pandoc -t gfm --wrap=none` (`ACOMPAS-IA/acompas-fuentes#6`). Cambian los saltos de línea de cinco fuentes, no su texto: ninguna pieza cambia de contenido.

**Nota sobre ADR-013:** la fuente es `docs/adr/ADR-013-politica-de-anonimizacion-y-umbral.md` del commit indicado. El fichero suelto `ADR-013.md` de `~/projects/acompas-fuentes/` no es fuente, y su texto difiere en una consecuencia.

**Nota sobre las fichas:** en `4275ef0`, ocho fichas (ACO-013, 014, 019, 022, 023, 024, 025 y 026) declaran sus criterios confirmados en la revisión de su PR, con el número de la PR. ACO-032 conserva el literal «pendientes de confirmar en la revisión de la PR» porque su corrección va en #149, abierta. 08-PLAN §5 describe ese estado y el INFORME lo recoge como cuestión pendiente.

**Nota sobre ADR-015:** su contexto afirma que la demo interna del 27/10/2026 se celebró. No se celebró. El ADR está aprobado y no se edita; el arnés no compila esa premisa (INFORME, PD-26).

**Nota sobre ADR-016, ADR-017 y ADR-018:** los tres están aprobados y constan en el registro del Plan de Trabajo v0.12. ADR-017 abre una excepción temporal a ADR-009 (lista blanca en `.env` durante local y demo), y ADR-018 abre una excepción acotada a ADR-016 D1-A (aplicación del rol por defecto por la Admin API después de la importación). El arnés las recoge como reglas del Sprint 1, no como cambios permanentes del stack.

**Excluidas:** «ACOMPAS - Fichas ACO Sprint 1 v0.2» (la fuente de las fichas es `docs/aco/`); `ADR-013.md` suelto; contenido de ramas sin fusionar (entre otras, la PR #149 y la PR #162); los demás .docx; el AGENTS.md y los ficheros del arnés anterior; el código; la Guía del método del arnés; el Calendario de Acciones; versiones anteriores de cualquier documento.

## 3. Condiciones previas (Estrategia §4.3)

Son las condiciones de la primera generación (modo A). En esta regeneración se han vuelto a comprobar, y su resultado no la bloquea:

| Condición | Resultado en el modo B | Evidencia |
|---|---|---|
| ADR aprobados | Cumple | ADR-001 a ADR-018 tienen «Estado: aprobado», y el registro del Plan de Trabajo v0.12 incluye ADR-001 a ADR-018 |
| Contradicciones conocidas cerradas | Las conocidas no detienen ninguna pieza | El Modelo E/R v0.10 alinea los estados del glosario, las etiquetas de persona y el tratamiento del documento retenido (02-DOMINIO §5). ADR-016 y ADR-018 resuelven el rol por defecto y los tokens offline; ADR-017, el mecanismo de la lista blanca. Quedan discrepancias menores de redacción en los Casos de Uso y el wireframe 4, sin efecto en las reglas (INFORME) |
| Modelo E/R alineado con los ADR | Cumple en los tres puntos que estaban abiertos | Los estados, las etiquetas y el documento retenido coinciden con ADR-013 y la Arquitectura §4; la dimensión 768 queda marcada como provisional (Arquitectura §16 nº 14) |

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
| `02-DOMINIO.md` | Arquitectura §4, §6, §7, §8, §9, §16; ADR-001, 002, 003, 005, 006, 007, 009, 010, 011, 012, 013, 014, 017 | Casos de Uso §1–§3; Modelo E/R §1, §2, §3, §4; fichas ACO-022 y ACO-023 (qué fija cada una en la política y la numeración) |
| `03-REGLAS.md` | ADR-001 a 018; Arquitectura §2, §3, §4, §5, §6, §8, §9, §10, §11, §13, §14, §15, §16; Plan de Proyecto §1, §2; Plan de Trabajo §2, §4, §5, §8, §9, §10 | Casos de Uso UC-05, UC-07, UC-09; Fichas ACO-012, 014, 015, 021, 022, 023, 024, 025, 028, 031, 051 |
| `04-INTERFAZ.md` | Plan de Proyecto §1, §4, §6; Arquitectura §3, §4, §6, §7, §8, §9, §11, §14; ADR-012, ADR-013 | Casos de Uso UC-01, 03–06, 08–13, 17, 18, 20–24; Wireframes, pantallas 1–10 (incluidas 4b, 4c y la vista móvil); fichas ACO-017, ACO-031 y ACO-032 |
| `05-DISEÑO.md` | Arquitectura §3–§11, §13, §14, §16; Plan de Proyecto §2; ADR-001, 003, 004, 005, 006, 007, 009, 010, 011, 012, 013, 014, 015, 016, 017, 018 | Wireframes (componentes de interfaz); Modelo E/R (persistencia) |
| `06-SEMILLA.md` | Plan de Proyecto §2; Arquitectura §4, §6, §11; ADR-008, 009, 011, 012, 013, 016, 017, 018 | Fichas ACO-012, 015, 051, 052 |
| `07-INTERCAMBIO.md` | Arquitectura §3, §4, §5, §6, §8, §11, §13, §16; ADR-001, 003, 004, 005, 006, 009, 011, 012, 013, 014, 015, 016, 017, 018 | Modelo E/R §2, §3, §4; Casos de Uso UC-03, UC-07, UC-09; Fichas ACO-012, 014, 015, 019, 020, 021, 022, 023, 024, 025, 027, 028, 030, 032, 051 |
| `08-PLAN.md` | Plan de Proyecto §4; Plan de Trabajo §4, §6, §9, §10; Documento Operativo Sprint 1 §2, §6, §9, §10, §11, §12, §13, §14; Arquitectura §14, §16; ADR-013, ADR-014, ADR-015 (registro del Plan de Trabajo §9 y criterios D-03 y D-06) | Fichas ACO-011 a 033, 051, 052 (objetivo, incluye, fuera de alcance, estado y criterio de revisión); los ACO del Sprint 2 (035–046, 053–056) se citan solo como los nombra el Plan de Trabajo §6, sin ficha, y ACO-007 como lo documenta el Documento Operativo §6. Lo que procede de ADR-013 a ADR-018 se remite a 03 y 09 |
| `09-TESTS.md` | Plan de Proyecto §1; Arquitectura §4, §16; ADR-013, ADR-014, ADR-015; Documento Operativo Sprint 1 §3, §9, §14 | Casos de Uso; Modelo E/R; Wireframes 1, 4, 5; Fichas ACO-014, 015, 019–026, 028–033, 051, 052 (criterios y tests esperados); criterios D-01…D-07 vía 08-PLAN |
| `AGENTS.md` (raíz) | Plan de Trabajo §4 (incluida «Ejecución de un ACO con un agente de IA»), §8, §9, §10; Estrategia §4.1 | — |

## 5. Cuestiones abiertas heredadas por pieza

| Cuestión abierta | Fuente | Piezas |
|---|---|---|
| Gestión de secretos en producción, rotación automática y escáner de secretos en CI | ADR-015 (Fuera de esta decisión) | 03 |
| Entorno de desarrollo: Docker Compose como base común y VPS solo cerca de la demo de diciembre. Decisión adoptada; falta redactar el ADR | Arquitectura §16 nº 11 | 03, 05, 08 |
| Encaje mínimo y alcance del LLM gateway en el Sprint 1 | Arquitectura §16 nº 12; ACO-027 | 03, 05, 07, 08 |
| Modelo de Claude y política de actualización | Arquitectura §16 nº 13 | 03, 05, 08 |
| Sprint del clasificador de intención | Arquitectura §16 nº 1 | 01, 03, 05 |
| Alternativa de almacenamiento de objetos | Arquitectura §16 nº 2; ADR-010 | 02, 03, 05 |
| Diseño del derecho al olvido | Arquitectura §16 nº 3 | 03, 04, 05, 07 |
| Modelo del registro de auditoría | Arquitectura §16 nº 4 | 02, 03, 05, 07 |
| Modelo de datos definitivo | Arquitectura §16 nº 5 | 02, 03 |
| Calendario y corpus del RAG en S3–S4 | Arquitectura §16 nº 6 | 01, 03, 05 |
| Comprobación del tipo de documento (clínico) antes de procesarlo | Arquitectura §16 nº 8 | 03, 05 |
| Confianza del OCR para detectar documentos ilegibles y umbrales en los Niveles 2 y 3 o con documentos reales | Arquitectura §16 nº 9 | 03, 05, 09 |
| Diseño del Nivel 3 (incluida la revisión obligatoria del documento retenido cuando exista) | Arquitectura §16 nº 10; ADR-013 | 02, 03, 04, 05 |
| Modelo de embeddings, dimensión y chunking. La dimensión 768 es provisional | Arquitectura §16 nº 14; ADR-007 | 02, 03, 05 |
| Motor de OCR definitivo (solo si Tesseract no rinde) | Arquitectura §16 nº 15 | 03, 05 |
| Regla de cálculo del crédito y topes | Arquitectura §16 nº 16 | 03, 05, 06 |
| Contratación y configuración del VPS | Arquitectura §16 nº 17 | 03, 05 |
| posicion_inicio y posicion_fin de ETIQUETA_ANONIMIZACION | Modelo E/R | 02, 07 |
| «Fuera de esta decisión» de ADR-001, 003, 011 y 012 | ADR correspondiente | 02, 03, 04, 06, 07 |
| «Fuera de esta decisión» de ADR-013: texto de los avisos al paciente (documento retenido e ilegible); nombre exacto de la etiqueta genérica de persona; catálogo de TIPO_ETIQUETA y de `tipo_entidad`. Los demás puntos son las cuestiones 8 a 10 de la Arquitectura §16 y la fila de reconocedores y filtros | ADR-013 | Avisos: 03, 04, 07. Etiqueta genérica y catálogos: 02, 06, 07 |
| «Fuera de esta decisión» de ADR-017: producción y uso con datos reales, SMTP y verificación de email, gestión completa de usuarios, la tabla `EMAIL_AUTORIZADO` y su migración (Sprint 2) | ADR-017 | 02, 03, 06, 07 |
| Formatos de entrada del Sprint 1 (texto frente a PDF o imagen) | Wireframes, pantalla 3; ACO-020; ACO-051 | 04, 07 |
| Contenido y límites de los campos de texto libre `motivo` y `motivo_resolucion` (pueden contener datos identificativos) | Modelo E/R (SOLICITUD_DESBLOQUEO_CREDITO); Wireframes 8 y 9 | 02, 03, 04, 07, 08 |
| Interfaz de la solicitud de borrado | Wireframes, pantalla 2; Arquitectura §16 nº 3 | 04 |
| Formato exacto del nombre genérico del documento | ADR-012 (Fuera de esta decisión); Wireframes 2, 3, 4 y 5 | 02, 04 |
| Emails de prueba, catálogos iniciales y valores de crédito iniciales | ACO-015; Modelo E/R; Arquitectura §16 nº 16 | 06 |
| Criterios pendientes en la ficha de ACO-032 (su línea de estado la corrige #149, abierta) | Ficha ACO-032; PR #149 | 08 |
| Lista concreta de reconocedores, filtros de falsos positivos y términos permitidos (fichas de ACO-022 y ACO-023 al ampliarse) | ADR-013 (Fuera de esta decisión); ACO-022; ACO-023 | 03, 07, 08, 09 |
| Correspondencia entre las categorías del manifiesto de ACO-051 y las categorías garantizadas (T-31) | ADR-013 (Consecuencias); ACO-051 | 09 |
| Registro de auditoría del documento retenido en el Sprint 1 (T-10) | ADR-013; Arquitectura §16 nº 4 | 09 |
| Alcance del Sprint 2 y matriz del traspaso de ACO-033 | Documento Operativo §6, §14; Plan de Trabajo §6 | 08 |
| Tono del LLM (D9) | Plan de Proyecto §1 | 01, 03, 09 |
| Objetivo de cobertura (más del 85%, Niveles 1–2) como métrica posterior | Arquitectura §4; ADR-003 | 03, 09 |

**Notas:** ACO-031 fija el punto del disclaimer (pie permanente de `AppShell`, slot `disclaimer`) y su texto literal; 04-INTERFAZ ya lo recoge, y las cuestiones de PD-27 y PD-29 quedan cerradas. Los motivos de la solicitud de desbloqueo ya están en el Modelo E/R v0.10; la cuestión de PD-30 queda cerrada, y en su lugar queda abierto el contenido y el límite de esos textos libres. El mecanismo de la lista blanca ya no es una cuestión abierta: lo resuelve ADR-017.

## 6. Detenciones

**Regeneración (modo B):** ninguna pieza se ha detenido. Las discrepancias que quedan entre las fuentes derivadas y las normativas son de redacción y no cambian ninguna regla (INFORME). Detalle en `INFORME-GENERACION.md`, sección «Regeneración (modo B) — pasada B (2026-11-13)».

**Regeneración (modo B) de 2026-11-02:** ninguna pieza se detuvo. La cuestión 7 de la Arquitectura §16 quedó cerrada por ADR-014, y la gestión de la API key, por ADR-015.

**Primera generación (modo A):**

Ninguna pieza se ha detenido. Las discrepancias detectadas se resolvieron con la prevalencia de la fuente normativa sobre la derivada (Estrategia §4.6 y §9), por decisión del usuario en el PLAN, o se recogieron como cuestión abierta. Detalle en `INFORME-GENERACION.md`.
