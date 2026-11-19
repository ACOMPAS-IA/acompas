# Registro de seguimientos

> Lo que pide el Plan de Trabajo §4 y lo que sustituye a la lista de Issues con
> la etiqueta «pendiente documental» (Estrategia de Actualización Documental,
> sección 3, regla 4). Una fila por hallazgo o advertencia, escrita en la misma
> PR que lo encuentra. El porqué de la medida y la comparación que la motivó
> están al final, en «Por qué existe este registro».

## El grano y el vocabulario

El grano es **una fila por ítem**, no por documento: dos hallazgos en el mismo
documento son dos filas.

Entra en el registro todo hallazgo o advertencia que **no tenga decisión
propia**. No entra lo que ya tiene vehículo —el bloqueo, lo que queda fuera de
alcance y el hallazgo o la advertencia que exigen una decisión—: eso abre
Issue, y una fila del registro no la sustituye ni amplía el alcance de una
ficha (Plan de Trabajo §4).

Los dos nombres. La Estrategia llama «pendientes» a las filas y el Plan de
Trabajo las llama «hallazgos y advertencias»; son la misma cosa. Aquí
«pendiente» nombra la lista y «hallazgo o advertencia» nombra lo que se apunta,
y las dos palabras valen al hablar del registro.

## Qué lleva una fila

| Columna | De dónde sale |
| --- | --- |
| Sprint | El sprint en que nació la fila. No es el sprint en que se arregla: una fila puede cruzar de uno a otro. |
| Fecha | El día en que se abrió. |
| Documento afectado | Documento y sección, con su versión: «Plan de Trabajo v0.15, §4». |
| Qué falta | Una frase: qué dice la fuente y qué debería decir. |
| Dónde se arregla | El vehículo concreto: la sección que hay que tocar, el documento que la sustituye o la PR que lo aplica. |
| Estado | `abierta`, `en PR` o `cerrada`. |
| PR | Mientras la fila está abierta, la PR que la encontró, con su repositorio. Al cerrarse, la PR que la arregló. |

Una fila sin «dónde se arregla» está a medio escribir: si no se sabe dónde, es
que todavía no es un seguimiento, sino una queja.

## El ciclo de una fila

- **Abierta, en PR y cerrada.** Se abre en la PR que la encuentra, pasa a «en PR» cuando existe la PR que la arregla y a «cerrada» cuando esa PR entra en `main`.
- **No se borra.** Una fila cerrada se queda con la PR que la cerró: es el rastro de que el problema existió y de cómo se resolvió.
- **Un solo registro.** No se parte por sprints: cada fila lleva el sprint en que nació, y la que sobrevive al cierre se queda y se vuelve a repasar en el siguiente.
- **Fila nacida en otro repositorio.** Si el hallazgo aparece en una PR de otro repositorio, la fila va en la PR de `acompas` que encargó el cambio. Si esa PR ya está mergeada, la PR de origen la escribe en su cuerpo y entra aquí en la primera PR de `acompas` posterior. Así nacieron las tres filas de la tabla: vienen de #13, en `acompas-fuentes`, y entran con la PR que crea este fichero.

## Tabla

| Sprint | Fecha | Documento afectado | Qué falta | Dónde se arregla | Estado | PR |
| --- | --- | --- | --- | --- | --- | --- |
| S2 | 18 nov 2026 | Documento Operativo Sprint 2 v0.3, §15 | Dice que los seguimientos son «defectos y hallazgos que hay que arreglar»; el registro recoge también advertencias, y una advertencia no siempre se arregla | Próxima revisión del Documento Operativo Sprint 2, §15 | abierta | [#13](https://github.com/ACOMPAS-IA/acompas-fuentes/pull/13) |
| S2 | 18 nov 2026 | Plan de Trabajo v0.15, §4, «Fila nacida en otro repositorio» | Habla solo de «el hallazgo»; el registro recoge hallazgos y advertencias | Próxima revisión del Plan de Trabajo, §4 | abierta | [#13](https://github.com/ACOMPAS-IA/acompas-fuentes/pull/13) |
| S2 | 18 nov 2026 | Plan de Trabajo v0.15, §4, «Ciclo de una fila» | Al mudar la regla desde el Documento Operativo se perdió «como historial»: por qué la fila no se borra queda implícito | Próxima revisión del Plan de Trabajo, §4 | abierta | [#13](https://github.com/ACOMPAS-IA/acompas-fuentes/pull/13) |
| S2 | 18 nov 2026 | ADR-015, §Contexto y §Decisión, punto 2 | Afirma dos veces que la demo del 27/10/2026 se hizo con una clave personal, y sitúa en esa fecha el hito del que quedó fuera ACO-028; el hito pasó al 9 de noviembre (Plan v0.11) y la demo no se celebró | ADR de sustitución de ADR-015: el Plan §9 no permite editar un ADR aprobado ni prevé corregir una errata | abierta | [#95](https://github.com/ACOMPAS-IA/acompas/pull/95) |
| S2 | 18 nov 2026 | Casos de Uso v0.7, UC-08 y UC-09 | No describe la conversación sin documento que aprobó la decisión #145: UC-08 presupone «su propio historial clínico», UC-09 solo cubre el origen de la respuesta y UC-10 habla de recargar la documentación | Casos de Uso, próxima revisión (UC-08, UC-09 o un caso nuevo), antes de ampliar la ficha del ACO de #145; después se regenera el arnés | abierta | — (origen: [#145](https://github.com/ACOMPAS-IA/acompas/issues/145)) |
| S2 | 18 nov 2026 | Plan de Trabajo v0.15, §8 | No recoge la regla de agrupar en la PR abierta el cambio que encaja en ella; el arnés la aplica por la decisión registrada en #164 | Próxima revisión del Plan, §8 | abierta | [#164](https://github.com/ACOMPAS-IA/acompas/pull/164) |
EAD
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 9 | La cuestión de la confianza del OCR y los umbrales sigue abierta después del merge de ADR-023, y esa sección es la fuente única de las cuestiones abiertas | Próxima revisión de la Arquitectura, §16 | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 15 | La cuestión del motor de OCR definitivo sigue abierta después del merge de ADR-023, y esa sección es la fuente única de las cuestiones abiertas | Próxima revisión de la Arquitectura, §16 | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Arnés 03-REGLAS, 05-DISEÑO, 09-TESTS y MANIFIESTO | Listan la confianza del OCR como cuestión abierta que alimenta 03, 05 y 09, y el motor definitivo, que solo alimenta 03 y 05; caen cuando ADR-023 entre y la Arquitectura retire §16 nº 9 y nº 15 | Regeneración del arnés, después de la revisión de la Arquitectura | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Arnés 04-INTERFAZ, «Cuestiones abiertas» | El wireframe 3 anuncia PDF, JPG y PNG, pero el pipeline del Sprint 1 trabaja sobre texto; ADR-023 fija los formatos del Sprint 2, así que la fila se reescribe al regenerar | Regeneración del arnés, que retira la fila al recoger el ADR | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Plan de Trabajo v0.15, §9 | El registro de ADR llega a ADR-018: faltan los ADR desde el 019; al regenerar caen también las listas de ADR que hoy llegan a 018 (arnés 03, 05 y 06, y el manifiesto) | Próxima revisión del Plan, §9, y regeneración del arnés | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 4 | La cuestión del modelo del registro de auditoría sigue abierta después de ADR-024, y esa sección es la fuente única de las cuestiones abiertas | Próxima revisión de la Arquitectura, §16 | abierta | [#193](https://github.com/ACOMPAS-IA/acompas/issues/193) |
| S2 | 19 nov 2026 | Arnés 02-DOMINIO, 03-REGLAS, 05-DISEÑO, 09-TESTS y MANIFIESTO | Listan la auditoría como cuestión abierta (`02:113`, `03:118,142`, `05:82`, `09:144`) y describen `AUDITORIA` con `detalle` y `creado_en`; caen cuando se actualicen las fuentes y se regenere el arnés desde ellas | Regeneración del arnés, después de la revisión de la Arquitectura | abierta | [#193](https://github.com/ACOMPAS-IA/acompas/issues/193) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16.4, y Documento Operativo Sprint 2 v0.4 | #81 pide la §16.4 actualizada en la misma actuación que el ADR; ADR-024 se mergea antes y la sección queda para el encargo posterior, porque este repositorio no edita fuentes | Encargo a `acompas-fuentes`, que se redacta al cerrar la PR de ADR-024 | abierta | [#193](https://github.com/ACOMPAS-IA/acompas/issues/193) |
| S2 | 19 nov 2026 | Documento Operativo Sprint 2 v0.4, §6, fila ACO-039 | Asigna 8–10 h a ACO-039, que no tiene ficha de alcance ni entrada en `docs/aco/sprints.toml`; el ADR ya le da modelo y dependencias | Ficha de ACO-039, antes de su BUILD | abierta | [#193](https://github.com/ACOMPAS-IA/acompas/issues/193) |
| S2 | 19 nov 2026 | Modelo E/R v0.10, §4 | El paso 9 manda borrar las filas de `AUDITORIA` del paciente; ADR-024 §6 y ADR-025 §7 las anonimizan con `audit_erasure`, y la secuencia del arnés (`07-INTERCAMBIO`) copia el paso 9 | Próxima revisión del Modelo E/R, §4; después, regeneración del arnés | abierta | — (origen: [#196](https://github.com/ACOMPAS-IA/acompas/issues/196)) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 3 | Sigue diciendo «ADR pendiente S2» y no recoge el resultado de ADR-025, que la resuelve; esa sección es la fuente única de las cuestiones abiertas | Próxima revisión de la Arquitectura, §16 | abierta | — (origen: [#196](https://github.com/ACOMPAS-IA/acompas/issues/196)) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §13 | Prevé copias de seguridad cifradas y ninguna fuente fija qué ocurre con ellas al ejercer el derecho al olvido; ADR-025 verifica el borrado sobre los datos vivos y lo declara fuera de su decisión | Próxima revisión de la Arquitectura, §13 y §16 nº 3 | abierta | — (origen: [#196](https://github.com/ACOMPAS-IA/acompas/issues/196)) |
| S2 | 19 nov 2026 | Documento Operativo Sprint 2 v0.4, §6, fila ACO-040 | Asigna 12–16 h a ACO-040, que no tiene ficha de alcance ni entrada en `docs/aco/sprints.toml`; ADR-025 le da el diseño y las dependencias | Ficha de ACO-040, antes de su BUILD | abierta | — (origen: [#196](https://github.com/ACOMPAS-IA/acompas/issues/196)) |
| S2 | 19 nov 2026 | Documento Operativo Sprint 2 v0.4, §6, filas ACO-055 y ACO-056 | Asigna 4–6 h a «Staging» y 6–8 h a la demo sin decir cómo conviven en la misma instancia que fija ADR-026; sin arranque en limpio, el ensayo y la demo se pisan | Fichas de ACO-055 y ACO-056, antes de su BUILD; ADR-026, punto 4, fija el arranque en limpio | abierta | — (origen: [#198](https://github.com/ACOMPAS-IA/acompas/issues/198)) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 11 y nº 17 | Declara «ADR pendiente» en las dos cuestiones que ADR-026 resuelve, y §13 no recoge la configuración ni el reparto de entornos | Próxima revisión de la Arquitectura, §13 y §16 nº 11 y 17; después, regeneración del arnés | abierta | — (origen: [#198](https://github.com/ACOMPAS-IA/acompas/issues/198)) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 9 | La cuestión de la confianza del OCR y los umbrales sigue abierta después del merge de ADR-023, y esa sección es la fuente única de las cuestiones abiertas | Próxima revisión de la Arquitectura, §16 | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 15 | La cuestión del motor de OCR definitivo sigue abierta después del merge de ADR-023, y esa sección es la fuente única de las cuestiones abiertas | Próxima revisión de la Arquitectura, §16 | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Arnés 03-REGLAS, 05-DISEÑO, 09-TESTS y MANIFIESTO | Listan la confianza del OCR como cuestión abierta que alimenta 03, 05 y 09, y el motor definitivo, que solo alimenta 03 y 05; caen cuando ADR-023 entre y la Arquitectura retire §16 nº 9 y nº 15 | Regeneración del arnés, después de la revisión de la Arquitectura | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Arnés 04-INTERFAZ, «Cuestiones abiertas» | El wireframe 3 anuncia PDF, JPG y PNG, pero el pipeline del Sprint 1 trabaja sobre texto; ADR-023 fija los formatos del Sprint 2, así que la fila se reescribe al regenerar | Regeneración del arnés, que retira la fila al recoger el ADR | abierta | [#192](https://github.com/ACOMPAS-IA/acompas/pull/192) |
| S2 | 19 nov 2026 | Modelo E/R v0.10, `ETIQUETA_ANONIMIZACION` | `posicion_inicio` y `posicion_fin` siguen marcadas como cuestión abierta y el control de cambios de la v0.5 las llama «decisión definitiva»; ADR-022 las ancla al texto anonimizado (PD-03 del arnés) | Modelo E/R v0.11, encargo en `acompas-fuentes` | abierta | [#190](https://github.com/ACOMPAS-IA/acompas/pull/190) |
| S2 | 19 nov 2026 | Modelo E/R v0.10, `ADMINISTRADOR` | `keycloak_id` es `NOT NULL` sin `UNIQUE`; ADR-022 lo deja `UNIQUE NOT NULL` si lo resuelve el Plan de Trabajo §8 | Modelo E/R v0.11, junto con la anterior | abierta | [#190](https://github.com/ACOMPAS-IA/acompas/pull/190) |
| S2 | 19 nov 2026 | Modelo E/R v0.10, `DOCUMENTO` | No tiene campo para el hash del texto anonimizado que ADR-022 exige para detectar que las posiciones dejaron de ser válidas; solo existe el hash del fichero original | Modelo E/R v0.11, junto con las dos anteriores | abierta | [#190](https://github.com/ACOMPAS-IA/acompas/pull/190) |
| S2 | 19 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 5 | La cuestión del modelo de datos definitivo sigue abierta después del merge de ADR-022, y esa sección es la fuente única de las cuestiones abiertas | Próxima revisión de la Arquitectura, §16 | abierta | [#190](https://github.com/ACOMPAS-IA/acompas/pull/190) |
| S2 | 20 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 10 | Anuncia que el documento retenido pasará a revisión obligatoria cuando exista el Nivel 3; D2 bis de ADR-027 lo descarta, y llevarlo a revisión exige guardarlo temporalmente, que es una decisión de privacidad | Issue de decisión conjunta por el Plan de Trabajo §8 (privacidad), aún no abierta; después, revisión de la Arquitectura §16 nº 10 | abierta | — (origen: [#200](https://github.com/ACOMPAS-IA/acompas/issues/200)) |
| S2 | 20 nov 2026 | Plan de Proyecto v0.22, §4, Figura 1 | El único Gantt de las fuentes es una imagen incrustada en el `.docx` (`media/image1.png`): no tiene fuente editable y actualizarlo exige rehacer la figura | Próxima revisión del Plan de Proyecto, §4 | abierta | [#147](https://github.com/ACOMPAS-IA/acompas/pull/147) |
| S2 | 20 nov 2026 | Plan de Proyecto v0.22, §4 | Etiqueta el S1 como «sep–nov» y el S2 como «oct–dic»: se solapan en octubre y no son fechas de sprint, sino rangos de fase | Próxima revisión del Plan de Proyecto, §4 | abierta | [#147](https://github.com/ACOMPAS-IA/acompas/pull/147) |
| S2 | 23 nov 2026 | Arquitectura del Sistema v0.10, §10 y §13 | Declara «sin retención de datos» y garantía contractual de no retención ni uso para entrenamiento, pero el contrato no está en el repositorio y ninguna fuente fija cómo se comprueba; el procedimiento del olvido no puede alcanzar lo que ya se envió | Comprobar la garantía del contrato antes del primer uso con datos reales y concretarlo en la próxima pasada de fuentes si hay que matizarla | abierta | [#197](https://github.com/ACOMPAS-IA/acompas/pull/197) |
| S2 | 23 nov 2026 | Registro de desviaciones, fila del S2 | Dice «Sprint en planificación: sin matriz cerrada (DO Sprint 2 §6; #142)»; la matriz está cerrada desde el Documento Operativo v0.4, con 19 filas y ≈264 h | Fila del S2 de `docs/desviaciones.md`, que se rellena al cerrar el sprint | abierta | [#147](https://github.com/ACOMPAS-IA/acompas/pull/147) |
| S2 | 23 nov 2026 | Documento Operativo Sprint 2 v0.4, §6, fila de ACO-041 | La fila dice «Prompt injection: C13 de ACO-052 en ejecución real» y la ficha pasa a «Prompt v1: historial no fiable» por la revisión de #188, que da vehículo a la vía por prompt de #116; el resto de la fila (responsable, revisión, estimación, dependencias) no cambia | Próxima pasada de fuentes del Documento Operativo, §6 | abierta | [#188](https://github.com/ACOMPAS-IA/acompas/pull/188) |
| S2 | 25 nov 2026 | `backend/Dockerfile`, imagen del backend (ACO-034) | La imagen instala `.[dev]`: las dependencias de desarrollo viajan en producción y separarlas es una decisión de construcción que ACO-034 deja fuera de alcance | Próximo ACO que toque la imagen | abierta | [#208](https://github.com/ACOMPAS-IA/acompas/pull/208) |
| S2 | 25 nov 2026 | `.github/workflows/ci.yml`, job de pruebas del backend (ACO-034) | La CI descarga los modelos de anonimización en cada ejecución (unos 508 MB, ADR-020 §Contexto) y cachearlos es una decisión aparte | Próximo ACO que toque la CI | abierta | [#208](https://github.com/ACOMPAS-IA/acompas/pull/208) |

## Lo que no es este registro

- No es el registro de desviaciones (`docs/desviaciones.md`): las desviaciones son lo que se aparta de lo planificado —horas, alcance y fechas— y se anotan al cerrar el sprint; esto son huecos y defectos, y se anotan al encontrarlos.
- No es el control de cambios de los documentos: eso vive en cada documento.
- No sustituye la revisión de mitad de sprint (#168), que es donde se repasa (Documento Operativo Sprint 2 §9).
- No es la lista de tareas del sprint: recoge lo que hay que arreglar en la documentación, no el trabajo planificado.

## La lista anterior

El registro arranca el 18 de noviembre de 2026. Las Issues con la etiqueta
`pendiente documental` (PD-01 a PD-31) son la lista que este fichero sustituye.
Se migran comprobando cada una contra la fuente actual antes de escribir la
fila, y su Issue se cierra cuando la fila entra en `main`: una fila del registro
no afirma nada que no se haya verificado el día que se escribe. Las que ya
tienen vehículo —una PR abierta o un ADR— no se migran: se cierran donde se
resuelven. Hasta que se migren, el pendiente se lee en su Issue.

## Por qué existe este registro

El Sprint 1 se cerró con 96 Issues creadas y 53 abiertas al cerrar, 59 PRs
mergeadas de 64 y 79 rondas de revisión. Treinta y una de esas Issues eran PD y
follow-ups, y 18 de ellas seguían abiertas cinco semanas después de la pasada
que las generó. El problema no era la revisión: era cuántas cosas se convertían
en una Issue.

De ahí salen las tres medidas del Plan de Trabajo §4: el registro en vez de una
Issue por hallazgo, la revisión en tres bloques con dos rondas como máximo y las
decisiones por lotes. Este fichero es la primera.

La comparación completa, con su método y su ventana (1 de septiembre a 12 de
noviembre de 2026), está en la PR #11 de `acompas-fuentes`
(https://github.com/ACOMPAS-IA/acompas-fuentes/pull/11), que es donde se aprobó
el cambio. Son cifras de una medición con fecha, no un dato permanente: el
efecto de la medida se podrá medir en la revisión de mitad de sprint, que es
donde se repasa este registro (Documento Operativo Sprint 2 §9; #168).
