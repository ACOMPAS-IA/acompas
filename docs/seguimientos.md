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
| S2 | 20 nov 2026 | Arquitectura del Sistema v0.10, §16 nº 10; Casos de Uso v0.7, UC-06; Wireframes MVP v0.6, pantalla 4 | El Nivel 3 queda decidido en ADR-027 y las tres fuentes siguen diciendo que el documento retenido se descarta; la revisión obligatoria exige guardarlo temporalmente | Issue de decisión conjunta por el Plan de Trabajo §8 (privacidad), que abre la persona responsable; después, revisión de las tres fuentes | abierta | — (origen: [#200](https://github.com/ACOMPAS-IA/acompas/issues/200)) |

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
