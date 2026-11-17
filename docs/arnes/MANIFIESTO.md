# MANIFIESTO DE GENERACIÓN DEL ARNÉS

Artefacto compilado (Estrategia de Actualización Documental §4.2). Es el **único lugar** del arnés donde constan las versiones exactas de las fuentes.

## 1. Generación

| Campo | Valor |
|---|---|
| Modo | B: regeneración, ampliada el 2026-11-17 (anterior: modo B, 2026-11-02, commit `0a2d6f0`) |
| Fecha | 2026-11-13; ampliaciones del 16 y del 17 de noviembre de 2026 |
| Estado | **Regenerado y auditado, pendiente de revisión humana en PR**. Sin piezas detenidas. La ampliación del 16 de noviembre incorpora la retirada de la Guía rápida de revisión de PR (PD-11) y el estado de las fichas en `docs/aco/` tras #149 (`d92e8c4`), #162 (`68db567`) y #167 (`929daf8`): nueve fichas de la PD-25, ACO-015, ACO-028 y las fichas históricas ACO-001, ACO-006 y ACO-007. La ampliación del 17 de noviembre incorpora el Documento Operativo del Sprint 2 v0.1 (`acompas-fuentes` `5b5ca6d`) como fuente de 08 y 09: ventana y capacidad, matriz operativa con dos filas firmes, bloques sin ficha, trabajo identificado sin ACO, colchón y contingencia, y el traslado de D-07. Sin pendientes documentales: `docs/arnes/INFORME-GENERACION.md` recoge las tres secciones. **PD-24 cerrada el 17 de noviembre de 2026:** el Plan de Trabajo v0.12 incluye ADR-015 en el registro de ADR y la v0.13 lo confirma, así que la condición de ADR aprobados ya no tiene salvedad |
| Fuentes cambiadas | Plan de Proyecto (v0.21 → v0.22: §1, §6, §7); Arquitectura del Sistema (v0.9 → v0.10: §16); Plan de Trabajo (v0.11 → v0.12: §8, §9, §11, §12, §13); Documento Operativo Sprint 1 (v0.5 → v0.7: §6, §9, §10, §14, §16); Casos de Uso (v0.6 → v0.7: §2, §3, portada); Modelo E/R (v0.9 → v0.10: §1, §2); Wireframes MVP (v0.5 → v0.6: pantallas 2–5, 8, 9, nuevas 4b, 4c y 10); `docs/adr/` (ADR-016, ADR-017 y ADR-018, nuevos); 18 fichas ACO (ACO-012, 014, 015, 018, 019, 020, 021, 023, 024, 025, 026, 027, 028, 030, 031, 032, 033 y 052). La Estrategia v0.8 y las demás fuentes conservan versión (su SHA-256 es el de `85c0ab4`; el de la instantánea vigente `f7eff22` consta en §2, con las notas de forma). Después, en `68db567`, cambian las líneas de estado de nueve fichas, el encabezado de ACO-015 y la de ACO-028 (PD-25). En la ampliación del 16 de noviembre cambian el Plan de Trabajo (v0.12 → v0.13: §4, §11) y la Estrategia de Actualización Documental (v0.8 → v0.9: Anexo A), y la línea de estado de ACO-032 en `d92e8c4` (#149); en `929daf8` (#167) entran las fichas históricas ACO-001, ACO-006 y ACO-007. En la ampliación del 17 de noviembre entra el Documento Operativo del Sprint 2 (v0.1, nuevo: §5 ventana y capacidad, §6 matriz operativa, §7 paquetes de trabajo, §8 carga y colchón, §9 planificación, §11 riesgos, §12 decisiones pendientes y §14 criterios heredados) |
| Piezas regeneradas | 01, 02, 03, 04, 05, 06, 07, 08 y 09; en la ampliación del 16 de noviembre, 08 (§5, fichas) y `AGENTS.md` (§9); en la del 17, 08 (§2, §4 y la sección 7, Sprint 2) y 09 (§1, D-07) |
| Piezas sin regenerar | En la ampliación del 16 de noviembre, 01 a 07 y 09: la retirada de la Guía rápida de revisión de PR no cambia ninguna regla, ningún dato ni ningún contrato, y el cambio de `docs/aco/` solo afecta al estado de las fichas (08). En la del 17, 01 a 07: el Documento Operativo del Sprint 2 es fuente de planificación y verificación, y no introduce reglas. En la pasada B, `AGENTS.md` no se tocó porque sus fuentes (Plan de Trabajo §4, §8, §9 y §10; Estrategia §4.1) no cambiaban de contenido |
| Instantáneas de origen | Documentos de `~/projects/acompas-fuentes/` en `90acd3c` (13 nov 2026), publicados en `main` de `acompas-fuentes` en `85c0ab4`; la instantánea vigente de las fuentes es `5b5ca6d` (17 nov 2026), con `sha256sum -c SHA256SUMS`: 17/17. Entre `85c0ab4` y `f7eff22` solo hay cambios de forma (notas del §2); entre `f7eff22` y `89cadd4` cambian el Plan de Trabajo (v0.13) y la Estrategia (v0.9) y sale la Guía rápida de revisión de PR (PD-11); entre `89cadd4` y `5b5ca6d` entra el Documento Operativo del Sprint 2 v0.1 (`7696185`) y se retira su `.docx` (`acompas-fuentes#10`); `docs/adr/` y `docs/aco/` en `929daf8` (16 de noviembre, tras #162 y #167) |
| Commit de las fuentes del repositorio | `929daf8` para `docs/adr/` y `docs/aco/`, en `main`. Entre `a1df03b` y `68db567` se añaden ADR-016, ADR-017 y ADR-018; entran en ese commit las líneas de estado de ACO-013, 014, 019, 022, 023, 024, 025, 026, 015 y 028 (PD-25), la remisión a la matriz del Documento Operativo de ACO-020, 021 y 033, y la cita de la PR de fuentes en ACO-031. La línea de estado de ACO-032 la corrigió `d92e8c4` (#149), anterior. #167 (`929daf8`) añade las fichas históricas ACO-001, ACO-006 y ACO-007 y, fuera de `docs/aco/`, `sprints.toml`, `docs/indice.md`, `scripts/indice.py` y el job `docs` de la CI; no cambia ninguna regla, ningún dato ni ningún contrato |
| Proceso | Estrategia de Actualización Documental v0.9: §4.10 y Anexo B (modo B), con las reglas del modo A |

## 2. Fuentes congeladas

| Fuente | Versión exacta | Fichero leído | SHA-256 |
|---|---|---|---|
| Plan de Proyecto | v0.22 | `ACOMPAS - Plan de Proyecto v0.22.md` | `3d7fc2070c9686b5e9ad2805afe7f095d6be37d63ca7c7863ac0536ea41701c4` |
| Arquitectura del Sistema | v0.10 | `ACOMPAS - Arquitectura del Sistema v0.10.md` | `b8c47bdffb2654473c5380622232cefdce8b57dcd812dc479299f1b644a005c2` |
| Plan de Trabajo | v0.13 | `ACOMPAS - Plan de Trabajo v0.13.md` | `f41461f72b5a36e3fd4cc28e2d89f066e6b3f0da32151ea78f05cef1238dff52` |
| Documento Operativo Sprint 1 | v0.7 | `ACOMPAS - Documento Operativo Sprint 1 v0.7.md` | `279d34241d3158a859d36ea7f32303443070504124980aa6d2933e965613a409` |
| Documento Operativo Sprint 2 | v0.1 | `ACOMPAS - Documento Operativo Sprint 2 v0.1.md` | `77d35556bcd9f80f12801894f01b488c88cb5de3ecc06a8c244ce6379c3009bf` |
| Casos de Uso | v0.7 | `ACOMPAS - Casos de Uso v0.7.md` | `9b43a423dfdddd5c8dcb3f87b14a1474b1cbc2da40a86b576ee5f1306c09e1f7` |
| Modelo E/R | v0.10 | `ACOMPAS - Modelo ER v0.10.md` (ver nota) | `11110481b8c6332e759419319adcb29600762d17bfc552437d84eb058c724013` |
| Wireframes MVP | v0.6 | `ACOMPAS - Wireframes MVP v0.6.html` | `b4d63f90de233b7353da077f084a0778ee0d2b877234518cf46ecdc27fc72912` |
| Estrategia de Actualización Documental | v0.9 | `ACOMPAS - Estrategia de Actualizacion Documental v0.9.md` (§4, incluida §4.10, y Anexos A y B) | `a28828250dabb9564bbf00e8da6f297ba964ed4192089cafb9d22571f7dbee78` |
| ADR aprobados | ADR-001 a ADR-018, todos «aprobado» | `docs/adr/` en el commit `929daf8` | — |
| Fichas ACO | ACO-001, 006 y 007 (históricas), ACO-011 a ACO-033, ACO-051 y ACO-052 (28 fichas) | `docs/aco/` en el commit `929daf8` (`PLANTILLA.md` y `sprints.toml` no son ficha ni fuente) | — |

Ficheros de `~/projects/acompas-fuentes/`.

**Nota sobre el Modelo E/R:** en la instantánea `90acd3c`, al convertirse a Markdown, las tablas de entidades perdieron las columnas Tipo, Restricción y Descripción, y por autorización expresa del usuario en el PLAN se leyeron del .docx **de la misma versión**. Corregido en `ACOMPAS-IA/acompas-fuentes#4` (PD-04): el `.md` de `f7eff22` conserva las cuatro columnas y es la única fuente que se cita. El contenido compilado en las piezas es el mismo.

**Nota sobre la exportación:** los `.md` de `f7eff22` se exportan todos con `pandoc -t gfm --wrap=none` (`ACOMPAS-IA/acompas-fuentes#6`). Cambian los saltos de línea de cinco fuentes, no su texto: ninguna pieza cambia de contenido.

**Nota sobre el Documento Operativo del Sprint 2:** es el único documento fuente que se redacta en Markdown y no tiene `.docx`. Su `.md` es original, no exportación: sus encabezados son suyos y no dependen de ninguna plantilla de Word. El `.docx` se retiró en `5b5ca6d` (`ACOMPAS-IA/acompas-fuentes#10`) porque es el `.md` lo que lee el arnés.

**Nota sobre ADR-013:** la fuente es `docs/adr/ADR-013-politica-de-anonimizacion-y-umbral.md` del commit indicado. El fichero suelto `ADR-013.md` de `~/projects/acompas-fuentes/` no es fuente, y su texto difiere en una consecuencia.

**Nota sobre las fichas:** en `docs/aco/` en `929daf8`, nueve fichas (ACO-013, 014, 019, 022, 023, 024, 025, 026 y 032) declaran sus criterios confirmados en la revisión de su PR, con el número de la PR; el encabezado de ACO-015 pasa a «Puntos de la revisión de la PR #125» y ACO-028 declara los suyos confirmados (#103). Ninguna ficha conserva un estado pendiente. ACO-032 lo hizo en `d92e8c4` (#149) y remite a esa PR la presentación del resultado (P8, §8.4 y criterios 12–14). Los commits `7cc69b9`, `be79c6e`, `4275ef0` y `58fac86` de la rama `docs/pasada-b-fichas` no están en `main`: su contenido entró aplastado en `68db567`, incluido en la instantánea citada. En `929daf8` (#167) entran además las fichas históricas ACO-001, ACO-006 y ACO-007, que declaran «Estado: ficha histórica» y no reconstruyen criterios de aceptación, estimación, responsable, revisión ni dependencias.

**Nota sobre ADR-015:** su contexto afirma que la demo interna del 27/10/2026 se celebró. No se celebró. El ADR está aprobado y no se edita; el arnés no compila esa premisa (INFORME, PD-26).

**Nota sobre ADR-016, ADR-017 y ADR-018:** los tres están aprobados y constan en el registro del Plan de Trabajo v0.13. ADR-017 abre una excepción temporal a ADR-009 (lista blanca en `.env` durante local y demo), y ADR-018 abre una excepción acotada a ADR-016 D1-A (aplicación del rol por defecto por la Admin API después de la importación). El arnés las recoge como reglas del Sprint 1, no como cambios permanentes del stack.

**Excluidas:** «ACOMPAS - Fichas ACO Sprint 1 v0.2» (la fuente de las fichas es `docs/aco/`); `ADR-013.md` suelto; contenido de ramas sin fusionar; el índice de ACO (`docs/indice.md`, `scripts/indice.py` y el job `docs` de `.github/workflows/ci.yml`) y `sprints.toml`, que entraron con #167 (`929daf8`): son la lista canónica de ACO y su comprobación, pero no son fuente del arnés; los demás .docx; el AGENTS.md y los ficheros del arnés anterior; el código; la Guía del método del arnés; el Calendario de Acciones; versiones anteriores de cualquier documento.

## 3. Condiciones previas (Estrategia §4.3)

Son las condiciones de la primera generación (modo A). En esta regeneración se han vuelto a comprobar, y su resultado no la bloquea:

| Condición | Resultado en el modo B | Evidencia |
|---|---|---|
| ADR aprobados | Cumple | ADR-001 a ADR-018 tienen «Estado: aprobado», y el registro del Plan de Trabajo v0.13 incluye ADR-001 a ADR-018 |
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
| `08-PLAN.md` | Plan de Proyecto §4; Plan de Trabajo §4, §6, §9, §10; Documento Operativo Sprint 1 §2, §6, §9, §10, §11, §12, §13, §14; Documento Operativo Sprint 2 §5, §6, §8, §9, §11, §12, §14; Arquitectura §14, §16; ADR-013, ADR-014, ADR-015 (registro del Plan de Trabajo §9 y criterios D-03 y D-06) | Fichas ACO-001, 006 y 007 (históricas: estado y objetivo) y ACO-011 a 033, 051, 052 (objetivo, incluye, fuera de alcance, estado y criterio de revisión); los ACO del Sprint 2 (035–046, 053–056) se citan solo como los nombra el Plan de Trabajo §6, sin ficha, y ACO-007 con su ficha histórica y el Documento Operativo §6. La matriz del Sprint 2 se cita del Documento Operativo y no de la Issue #142. Lo que procede de ADR-013 a ADR-018 se remite a 03 y 09 |
| `09-TESTS.md` | Plan de Proyecto §1; Arquitectura §4, §16; ADR-013, ADR-014, ADR-015; Documento Operativo Sprint 1 §3, §9, §14; Documento Operativo Sprint 2 §14 (D-07 heredado, con ACO-033 como vehículo) | Casos de Uso; Modelo E/R; Wireframes 1, 4, 5; Fichas ACO-014, 015, 019–026, 028–033, 051, 052 (criterios y tests esperados); criterios D-01…D-07 vía 08-PLAN |
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
| Lista concreta de reconocedores, filtros de falsos positivos y términos permitidos (fichas de ACO-022 y ACO-023 al ampliarse) | ADR-013 (Fuera de esta decisión); ACO-022; ACO-023 | 03, 07, 08, 09 |
| Correspondencia entre las categorías del manifiesto de ACO-051 y las categorías garantizadas (T-31) | ADR-013 (Consecuencias); ACO-051 | 09 |
| Registro de auditoría del documento retenido en el Sprint 1 (T-10) | ADR-013; Arquitectura §16 nº 4 | 09 |
| Alcance del Sprint 2 y matriz del traspaso de ACO-033 | Documento Operativo §6, §14; Plan de Trabajo §6 | 08 |
| Tono del LLM (D9) | Plan de Proyecto §1 | 01, 03, 09 |
| Objetivo de cobertura (más del 85%, Niveles 1–2) como métrica posterior | Arquitectura §4; ADR-003 | 03, 09 |

**Notas:** ACO-031 fija el punto del disclaimer (pie permanente de `AppShell`, slot `disclaimer`) y su texto literal; 04-INTERFAZ ya lo recoge, y las cuestiones de PD-27 y PD-29 quedan cerradas. Los motivos de la solicitud de desbloqueo ya están en el Modelo E/R v0.10; la cuestión de PD-30 queda cerrada, y en su lugar queda abierto el contenido y el límite de esos textos libres. El mecanismo de la lista blanca ya no es una cuestión abierta: lo resuelve ADR-017.

## 6. Detenciones

**Regeneración (modo B):** ninguna pieza se ha detenido. Las discrepancias que quedan entre las fuentes derivadas y las normativas son de redacción y no cambian ninguna regla (INFORME). Detalle en `INFORME-GENERACION.md`, secciones «Regeneración (modo B) — pasada B (2026-11-13)» y «Ampliación (modo B) — 16 de noviembre de 2026».

**Regeneración (modo B) de 2026-11-02:** ninguna pieza se detuvo. La cuestión 7 de la Arquitectura §16 quedó cerrada por ADR-014, y la gestión de la API key, por ADR-015.

**Primera generación (modo A):**

Ninguna pieza se ha detenido. Las discrepancias detectadas se resolvieron con la prevalencia de la fuente normativa sobre la derivada (Estrategia §4.6 y §9), por decisión del usuario en el PLAN, o se recogieron como cuestión abierta. Detalle en `INFORME-GENERACION.md`.
