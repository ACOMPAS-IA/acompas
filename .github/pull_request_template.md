## Qué

<!-- Qué cambia y por qué, en una o dos frases. -->

Closes #

Ficha: `docs/aco/ACO-XXX.md` <!-- o «no es un ACO» -->

## Qué conviene mirar

<!-- Dónde debe mirar quien revisa y por qué: el punto, la decisión o el riesgo
concreto. Una o dos frases, sin repetir el diff. (Plan de Trabajo §4) -->

## Decisiones delegadas

<!-- Decisiones técnicas que la ficha delega y que se han tomado. Si no hay, «ninguna». -->

## Avisos

Una fila por aviso. El destino es obligatorio: una Issue, un ADR, una ficha, una
fila del registro de seguimientos, o el motivo por el que no hay nada que hacer.

| Categoría | Detalle | Destino |
| --- | --- | --- |
| BLOQUEO | — | — |
| FUERA DE ALCANCE | — | — |
| HALLAZGO | — | — |
| ADVERTENCIA | — | — |

<!--
Destino: `#123`, `ADR-021`, `ficha ACO-058`, `fila en docs/seguimientos.md`, o
`— (sin acción: motivo)`.

Un hallazgo o una advertencia sin decisión propia no abre Issue: va como fila en
`docs/seguimientos.md`, en la misma PR que lo encuentra. Abren Issue el bloqueo,
lo que queda fuera de alcance y el hallazgo o la advertencia que exijan una
decisión (Plan de Trabajo §4).

Si no hay avisos, se deja cada fila con «—».
-->

## Comprobaciones

- [ ] La ficha del ACO está ampliada (si es un ACO)
- [ ] CI verde
- [ ] Sin secretos ni datos reales de pacientes
- [ ] Si ha intervenido un agente, el commit lleva una sola línea `Co-Authored-By`
