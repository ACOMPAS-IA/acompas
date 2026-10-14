# 09 — TESTS

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Verificaciones objetivas de las reglas (03-REGLAS) y de los criterios de aceptación (08-PLAN), con trazabilidad en los dos sentidos. Cada verificación `T-NN` indica qué regla o criterio cubre, cómo se comprueba y qué ACO la implementa. «Automatizable» significa que puede escribirse como test. «Revisión» significa que la comprueba la persona revisora de la PR.

## Qué no contiene

- El código de los tests ni los datos de prueba (ver 06-SEMILLA).
- Valores de umbral fijados en los tests: los tests los leen de la configuración (03-REGLAS R-13).
- Verificaciones de funcionalidades posteriores al Sprint 1 más allá de lo que debe preservarse.

## Fuentes

- **Normativas:** Plan de Proyecto (§1, §2, §4); Arquitectura del Sistema (§4, §8, §11, §13); ADR-001 a ADR-013; Documento Operativo del Sprint 1 (§3, §10, §14).
- **Derivadas:** Casos de Uso (UC-01, UC-03, UC-05, UC-06, UC-09); Modelo E/R (DOCUMENTO, ETIQUETA_ANONIMIZACION); Wireframes (pantallas 1, 4 y 5); Fichas ACO (criterios de aceptación y tests esperados: 014, 015, 019–026, 028–033, 051, 052); criterios de la demo D-01…D-07, que se toman de 08-PLAN.

## 1. Criterios de la demo del Sprint 1 → verificaciones

| Criterio (08-PLAN §1) | Verificaciones |
|---|---|
| D-01 Reproducibilidad | T-27 |
| D-02 Acceso | T-14, T-15, T-17 |
| D-03 Documento sintético | T-09, T-10, T-12, T-33, T-37 |
| D-04 No persistencia del original | T-03, T-04 |
| D-05 Conversación | T-01, T-18, T-21 |
| D-06 Calidad mínima | T-31 |
| D-07 Ingeniería | T-19, T-28, T-32 |

Hito *(Documento Operativo §14)*: lo cubre el conjunto D-01…D-07 ejecutado sobre el flujo de ACO-032 (T-32).

## 2. Verificaciones

| ID | Qué se comprueba | Cómo | Cubre | ACO |
|---|---|---|---|---|
| T-01 | No hay datos reales de pacientes en el código, los tests, los fixtures, los logs ni el repositorio. | Automatizable sobre el corpus (dominios de correo reservados, DNI de la lista permitida) + revisión de PR | R-01, R-02, R-05 · D-05 | Todos; 051 (AC-05) |
| T-02 | Los datos de prueba son sintéticos y cumplen las reglas de 06-SEMILLA §2. | Automatizable: tests de ACO-051 §12 (1–9) | R-02 | 051 |
| T-03 | El documento original no se escribe en la BD ni en almacenamiento persistente; solo queda el resultado anonimizado. | Automatizable: procesar un documento sintético y comprobar que no hay ficheros ni filas con su contenido original | R-03 · D-04 | 020, 021 (AC-06), 025, 026 |
| T-04 | Ni el contenido del documento original ni el nombre de su fichero aparecen en los logs ni en los mensajes de error. | Automatizable: capturar logs y errores durante el procesamiento de un documento sintético y buscar sus entidades del manifiesto y el nombre del fichero subido | R-04, R-05 · D-04 | 025, 026 |
| T-05 | No se guarda el valor original de las entidades detectadas. | Automatizable cuando exista persistencia (S2); en el S1, revisión | R-06 | S2 |
| T-06 | El documento guardado y mostrado lleva un nombre genérico, no el del fichero original. | Automatizable cuando exista persistencia; revisión de la interfaz | R-07 | S2+ |
| T-07 | Las etiquetas se numeran por documento: dos documentos con la misma persona producen numeraciones independientes. | Automatizable sobre la salida del anonimizador | R-08 | 022–024, 026 |
| T-08 | ACOMPAS no persiste el email del paciente ni la correspondencia email↔UUID. | Automatizable (esquema y datos tras el login) + revisión | R-10 | 015 |
| T-09 | Ningún documento llega a la conversación sin pasar por la anonimización. | E2E: el flujo de 032 no ofrece otra ruta | R-12 · D-03 | 032, 033 |
| T-10 | Un documento con confianza por debajo del umbral de documento se retiene: no pasa a la conversación, no se guarda ni el original ni el resultado anonimizado y se avisa al paciente. No queda rastro de su contenido ni de su nombre de fichero fuera del registro de auditoría (fecha, tipo de documento, motivo). | Automatizable con un caso sintético de baja confianza (el umbral se lee de la configuración, no se fija en el test) | R-13, R-49 · D-03 | 023, 025, 026, 033 |
| T-11 | La anonimización no llama a Claude API. | Automatizable: tests del pipeline sin red ni credenciales del LLM | R-14 | 020–024 |
| T-12 | La detección devuelve puntuaciones y se separa de la decisión de anonimizar. | Automatizable: tests de ACO-021 §12 (1–5) y de 022/023 | R-17 · D-03 | 021, 022, 023 |
| T-13 | La respuesta de la API de anonimización no contiene el texto original. | Automatizable: comparar la respuesta con las entidades del manifiesto sintético | R-18 | 024, 026 |
| T-14 | El login requiere 2FA vía Keycloak; no hay autenticación paralela. | E2E o prueba manual documentada + revisión | R-19 · D-02 | 012, 013, 018 |
| T-15 | El backend rechaza los tokens ausentes o inválidos y acepta uno válido. | Automatizable | R-20 · D-02 | 014 |
| T-16 | Un paciente no accede a recursos de otro paciente. | Automatizable cuando existan recursos por paciente | R-21 | S1: revisión; 014 |
| T-17 | Un email autorizado puede acceder y uno no autorizado es rechazado. | Automatizable o E2E | R-22 · D-02 | 015, 033 |
| T-18 | Ninguna llamada a Claude API se hace fuera del gateway. | Revisión de código + test que sustituye el cliente del gateway | R-23 · D-05 | 027, 030 |
| T-19 | La API key no está en el código fuente, en Git, en las respuestas HTTP, en los logs ni en el bundle del frontend. | Automatizable (búsqueda de patrones; inspección de respuestas) + revisión | R-24 · D-07 | 028 |
| T-20 | El prompt restringe al ámbito oncológico, rechaza instrucciones incrustadas e indica el origen de la respuesta. | Casos de ACO-052 (fuera de alcance, prompt injection) ejecutados en la demo | R-25, R-26, R-28 | 029, 030, 052 |
| T-21 | El disclaimer es visible en la conversación y las respuestas no se presentan como diagnóstico. | E2E o revisión de la interfaz | R-27 · D-05 | 031, 033 |
| T-22 | Un fichero repetido por el mismo paciente se detecta y no se reprocesa; el mismo fichero de otro paciente no se marca como duplicado. | Automatizable cuando exista persistencia | R-09 | S2+ |
| T-23 | Cifrado en reposo y TLS 1.2+. | Revisión de la infraestructura | R-11 | S2+ / VPS |
| T-24 | El Sprint 1 no introduce Niveles 2 y 3 ni OCR externo. | Revisión de PR | R-15, R-16 | 020–026 |
| T-25 | El control de gasto se aplica en el gateway. | Automatizable cuando se implemente | R-29 | Por planificar |
| T-26 | No se introduce otra BD, MinIO, otra tecnología fuera del stack ni embeddings remotos. | Revisión de dependencias en la PR | R-30, R-31, R-32, R-34 | Todos |
| T-27 | `docker compose up -d --build` levanta el entorno y `/health` devuelve `{"status":"ok"}`. | Automatizable o manual, según el Documento Operativo §3 | R-33 · D-01 | Todos |
| T-28 | La PR viene de una rama `feature/` o `fix/` del ACO, su primer commit es la ampliación de la ficha, está enlazada a su ficha e Issue, tiene la CI verde, revisión de la otra persona y merge squash. | Revisión de PR y protección de la rama | R-35, R-36, R-37, R-42, R-51 · D-07 | Todos |
| T-29 | No se toman decisiones conjuntas ni se crean ADR implícitos dentro de un ACO, las decisiones delegadas por la ficha se quedan en sus límites y constan en la PR, y no se desactivan controles de seguridad. | Revisión de PR | R-38, R-39, R-40, R-43, R-52 | Todos |
| T-30 | Los contratos entre módulos están documentados antes de la integración en 032. | Revisión: los contratos de 019, 024 y 030 existen documentados | R-41 | 019, 024, 030, 032 |
| T-31 | Ninguna entidad del manifiesto sintético de las categorías garantizadas se escapa en el flujo completo. Se comprueba que el dato ha desaparecido, no el rol asignado. Las categorías sin garantía no cuentan. | Automatizable: anonimizar los documentos de ACO-051 y comprobar que ninguna entidad del manifiesto de las categorías garantizadas sigue en la salida | R-44, R-45 · D-06 | 026, 033, 051, 052 |
| T-32 | Caso feliz E2E, usuario no autorizado y documento que no valida (si el flujo lo contempla), en la CI o con la dependencia documentada. El flujo de la demo contempla el documento retenido y el ilegible (D-03). | Automatizable (ACO-033) | D-07; hito | 032, 033 |
| T-33 | Una detección por debajo del umbral de hallazgo se descarta como ruido; una que lo supera y pasa los filtros se anonimiza, aunque su puntuación no sea alta. | Automatizable con casos sintéticos (el umbral se lee de la configuración) | R-13 · D-03 | 023, 026 |
| T-34 | Se conservan las fechas que no son de nacimiento, la edad, el sexo, la profesión y el país, y los filtros de falsos positivos no ocultan contenido clínico (nombres de pruebas, resultados, variantes genéticas). | Automatizable con casos sintéticos | R-46 | 023, 026 |
| T-35 | Las personas reciben la etiqueta de su rol cuando se puede determinar (con prevalencia del contexto sobre el modelo) y la genérica `[PERSONA_n]` cuando no. | Automatizable con los casos sintéticos de la ficha de ACO-022. El acierto de rol es un indicador de calidad: se mide y no bloquea | R-47 | 022, 026 |
| T-36 | Confianza del documento: un documento sin entidades de categorías garantizadas tiene confianza máxima y no se retiene; ni la duda sobre el rol ni las categorías sin garantía la rebajan. | Automatizable con la fórmula que documenta ACO-023 (el umbral se lee de la configuración) | R-45, R-48 | 023, 026 |
| T-37 | Un documento con texto extraído vacío no se procesa, y el aviso al paciente lleva un motivo distinto del de baja confianza. | Automatizable (unitario y E2E) | R-50 · D-03 | 023, 026, 033 |

## 3. Trazabilidad inversa (regla → verificación)

| Regla | Verificación | | Regla | Verificación |
|---|---|---|---|---|
| R-01 | T-01 | | R-23 | T-18 |
| R-02 | T-01, T-02 | | R-24 | T-19 |
| R-03 | T-03 | | R-25 | T-20 |
| R-04 | T-04 | | R-26 | T-20 |
| R-05 | T-01, T-04 | | R-27 | T-21 |
| R-06 | T-05 | | R-28 | T-20 |
| R-07 | T-06 | | R-29 | T-25 |
| R-08 | T-07 | | R-30 | T-26 |
| R-09 | T-22 | | R-31 | T-26 |
| R-10 | T-08 | | R-32 | T-26 |
| R-11 | T-23 | | R-33 | T-27 |
| R-12 | T-09 | | R-34 | T-26 |
| R-13 | T-10, T-33 | | R-35 | T-28 |
| R-14 | T-11 | | R-36 | T-28 |
| R-15 | T-24 | | R-37 | T-28 |
| R-16 | T-24 | | R-38 | T-29 |
| R-17 | T-12 | | R-39 | T-29 |
| R-18 | T-13 | | R-40 | T-29 |
| R-19 | T-14 | | R-41 | T-30 |
| R-20 | T-15 | | R-42 | T-28 |
| R-21 | T-16 | | R-43 | T-29 |
| R-22 | T-17 | | R-44 | T-31 |
| | | | R-45 | T-31, T-36 |
| | | | R-46 | T-34 |
| | | | R-47 | T-35 |
| | | | R-48 | T-36 |
| | | | R-49 | T-10 |
| | | | R-50 | T-37 |
| | | | R-51 | T-28 |
| | | | R-52 | T-29 |

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| T-31: el manifiesto de ACO-051 no distingue las categorías garantizadas. `DATE_TIME` mezcla la fecha de nacimiento (garantizada) con otras fechas (que no se anonimizan), y `TERRITORIO` mezcla la localidad (garantizada) con la provincia, que ADR-013 no menciona. No está definido cómo se identifican en el manifiesto las entidades que T-31 debe comprobar. | ADR-013 (Consecuencias); ACO-051 §8 |
| T-10: ADR-013 exige un registro de auditoría del documento retenido, pero el modelo del registro de auditoría está abierto y la auditoría completa queda fuera del Sprint 1. No está definido qué registro debe comprobarse en el Sprint 1. | ADR-013; Arquitectura §16 nº 4; Plan de Trabajo §11 |
| T-34 depende de la lista concreta de filtros de falsos positivos y términos permitidos, que fijan las fichas de ACO-022 y ACO-023. | ADR-013 (Fuera de esta decisión) |
| Si los umbrales cambian en los Niveles 2 y 3 o con documentos reales, y el uso de la confianza del OCR para detectar documentos ilegibles: las verificaciones del Sprint 1 no lo cubren. | Arquitectura §16 nº 9 |
| T-20 depende de los casos de ACO-052, cuyos criterios están pendientes de revisión; el tono (D9) no tiene criterio verificable cerrado. | ACO-052; Plan de Proyecto §1 |
| Objetivo de cobertura (más del 85% en los Niveles 1–2): es un objetivo del módulo, no criterio del Sprint 1, y su medición (métricas) es posterior. | Arquitectura §4 |
