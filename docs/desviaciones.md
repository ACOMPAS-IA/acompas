# Registro de desviaciones

> Registro que pide la decisión conjunta #144 (punto D). Una fila por sprint.
> Se rellena al cerrar el sprint, no durante: los valores intermedios son
> planificación, no desviación.

## Qué mide

| Columna | De dónde sale |
| --- | --- |
| Estimado | Suma de las estimaciones de la matriz operativa del Documento Operativo del sprint. Es esfuerzo total estimado, no consumo semanal. |
| Entregado al cierre | Suma de las estimaciones de los ACO que el Documento Operativo marca como entregados al cerrar. Los traspasados al sprint siguiente no cuentan. |
| Fin previsto | Fecha de cierre que fija el Documento Operativo al planificar el sprint. |
| Fin real | Fecha del acta de cierre del sprint. |
| Causa | Una frase: qué impidió cumplir lo estimado. Si no hay desviación, «—». |

Las dos cifras de horas se escriben en la misma unidad y con la misma fuente: si
el Documento Operativo cambia una estimación durante el sprint, la fila recoge
la vigente al cerrar y lo dice en la causa.

## Tabla

| Sprint | Estimado | Entregado al cierre | Fin previsto | Fin real | Causa |
| --- | --- | --- | --- | --- | --- |
| S1 | ≈143 h (Miguel ≈109 h, Luis ≈34 h) | ≈127–131 h: todo salvo ACO-033 (12–16 h), traspasado al S2 | 9 nov 2026 | 9 nov 2026 (demo); cierre registrado el 12 nov | ACO-033 no llegó: depende de `torch` en CPU y de los modelos horneados (#63, #117). Excepción autorizada en #137. |
| S2 | — | — | diciembre de 2026 | — | Sprint en planificación: sin matriz cerrada (#142). |

## Qué no es este registro

- No es el control de cambios de los documentos: eso vive en cada documento.
- No sustituye a la regla de recorte de #144 ni a la revisión de mitad de
  sprint (#168): recoge el resultado, no la decisión.
- No registra cambios de alcance. Un ACO que entra o sale de un sprint es una
  decisión conjunta (Plan de Trabajo §8) y se resuelve en su Issue.
