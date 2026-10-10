# ACOMPAS — Reglas para agentes de IA

> Parte del arnés de ACOMPAS (capa derivada). Se regenera, no se edita a mano. Recoge el comportamiento transversal del agente: jerarquía de fuentes, bloqueo, flujo de trabajo y revisión. No resume decisiones de producto. Las versiones exactas de sus fuentes constan en `docs/arnes/MANIFIESTO.md`.
>
> **Fuentes:** Plan de Trabajo (§4, incluido «Ejecución de un ACO con un agente de IA», y §8, §9, §10); Estrategia de Actualización Documental (§4.1, reglas del arnés).

## 1. Papel del agente

El agente puede analizar, proponer, implementar, ejecutar tests y preparar la PR. **La aceptación del cambio corresponde siempre a la revisión humana.** *(Plan de Trabajo §4)*

El agente ejecuta un ACO concreto. No redefine el proyecto, no amplía el alcance y no inventa requisitos.

## 2. Fuentes y prevalencia

El agente trabaja a partir de: *(Plan de Trabajo §4)*

1. la **Ficha ACO** asignada:
   - la **ficha de alcance** (`docs/aco/ACO-XXX.md`) contiene el objetivo, el alcance y los criterios de aceptación, sin responsable, estimación ni dependencias;
   - la **ficha ejecutable** es la ficha de alcance ampliada con la plantilla `docs/aco/PLANTILLA.md`;
2. la **matriz del Documento Operativo** del sprint en curso: responsable, revisión, estimación y dependencias;
3. el **arnés** (`docs/arnes/`): 01-PRODUCTO, 02-DOMINIO, 03-REGLAS, 04-INTERFAZ, 05-DISEÑO, 06-SEMILLA, 07-INTERCAMBIO, 08-PLAN y 09-TESTS.

Reglas de prevalencia:

- **Las fuentes oficiales prevalecen sobre las derivadas.** Una Ficha ACO o el arnés nunca cambian una decisión del Plan de Proyecto, de la Arquitectura del Sistema ni de un ADR aprobado. *(Plan de Trabajo §4; Estrategia §4.1)*
- En responsable, estimación y dependencias **prevalece la matriz del Documento Operativo** sobre la ficha. *(Plan de Trabajo §4)*
- **El arnés no decide:** es una compilación trazable, no una fuente de verdad. Si el arnés y una fuente oficial no coinciden, vale la fuente oficial y se informa de la discrepancia. *(Estrategia §4.1)*

## 3. Ficha ejecutable

*(Plan de Trabajo §4)*

- El responsable del ACO amplía la ficha de alcance al empezar el ACO, a mano o con un agente de IA. **La ampliación es el primer commit de la PR del ACO.**
- El revisor revisa primero la ficha ampliada y después el código.
- **El agente no empieza la fase BUILD sobre una ficha que no esté ampliada.**

## 4. Fases de ejecución

*(Plan de Trabajo §4)*

**PLAN.** Leer la ficha y la matriz; comprobar las dependencias; inspeccionar el código existente; identificar los cambios necesarios, los riesgos y las decisiones no especificadas. **El plan se presenta antes de modificar código.**

**BUILD.** Implementar exclusivamente el alcance de la ficha. Requiere la ficha ejecutable (§3).

**TEST.** Ejecutar los tests y comprobaciones correspondientes e informar de resultados, incidencias y bloqueos. Un ACO no se da por terminado porque el código parezca correcto, sino cuando los tests relevantes se han ejecutado y pasan.

## 5. Decisiones delegadas y dependencias nombradas

*(Plan de Trabajo §4, «Decisiones delegadas»)*

- **Decisiones delegadas.** La ficha ejecutable puede delegar en el agente decisiones técnicas acotadas, siempre que nombre explícitamente la decisión y sus límites (por ejemplo, la elección entre dos opciones concretas o un parámetro dentro de un rango). Dentro de esos límites, el agente decide sin bloquearse y **deja constancia de la decisión en la PR**.
- La delegación **nunca cubre** decisiones que requieren ADR (§7), decisiones conjuntas (§7) ni cuestiones de seguridad o privacidad.
- **Dependencias nombradas.** Una dependencia que la ficha ejecutable nombra expresamente (por ejemplo, una librería o un modelo concreto que el ACO necesita) queda autorizada por la revisión de la ficha. El agente no se bloquea por instalarla o usarla.
- Si la dependencia **añade, retira o sustituye un componente del stack**, sigue haciendo falta un ADR: la ficha no puede autorizarla por sí sola.

## 6. Categorías de lo que se informa

*(Plan de Trabajo §4)*

**Las cuatro categorías se recogen en la descripción de la PR. Solo BLOQUEO detiene el trabajo.**

### BLOQUEO

El agente se detiene, lo indica con **`BLOQUEO — <motivo>`** y explica qué decisión falta cuando:

- falta información necesaria;
- hay una contradicción entre documentos;
- necesita una decisión de arquitectura no definida ni delegada por la ficha;
- necesita una dependencia no aprobada ni nombrada en la ficha;
- tiene una duda relevante de seguridad o privacidad;
- el trabajo requiere modificar otro ACO;
- no puede cumplir los criterios de aceptación.

**Ante una decisión no especificada que la ficha no delega, se bloquea; no se inventa.** No se bloquea por una decisión que la ficha delega dentro de sus límites ni por una dependencia que la ficha nombra (§5).

**Cuestiones abiertas:** las que recoge el arnés siguen abiertas. Si una de ellas impide ejecutar el ACO, se convierte en BLOQUEO, no en una decisión automática. *(Estrategia §4.1)*

### FUERA DE ALCANCE

Un problema que pertenece a otro ACO no se resuelve en el actual: se señala como **`FUERA DE ALCANCE — requiere ACO-XXX`**.

### HALLAZGO

Un problema, inconsistencia o posible mejora detectado durante la ejecución que no impide cumplir el ACO ni pertenece a otro ACO. Por ejemplo, un defecto del código existente o una ambigüedad de la ficha resuelta de la forma más conservadora. Si su corrección está claramente dentro del alcance del ACO, el agente puede corregirla. Se informa como **`HALLAZGO — <descripción>`** en la descripción de la PR.

### ADVERTENCIA

Un riesgo o una suposición con la que el agente sigue adelante porque puede cumplir los criterios del ACO de forma segura y verificable, y que el revisor debe comprobar expresamente. Por ejemplo, la falta de información contextual o de documentación auxiliar. Se informa como **`ADVERTENCIA — <descripción>`** en la descripción de la PR, **de forma destacada**.

### Límites que no cambian

Además, el agente nunca: *(Estrategia §4.1)*

- elige valores que las fuentes no han decidido;
- modifica una fuente oficial para hacerla compatible con su trabajo;
- trata una Ficha ACO como autoridad para cambiar una decisión oficial;
- genera instrucciones o datos para pacientes reales cuando las fuentes exigen datos sintéticos;
- oculta una contradicción mediante una interpretación unilateral.

## 7. Decisiones

- Una decisión nueva no se consolida solo en un comentario de código. Si modifica el alcance o los criterios de un ACO, se actualiza su ficha; si es una decisión técnica, sigue el procedimiento de ADR. *(Plan de Trabajo §4)*
- **Requieren decisión conjunta** del equipo (Issue «decisión conjunta», 48 h para objetar), y por tanto son BLOQUEO para el agente (la única excepción son las dependencias que nombra la ficha ejecutable y que no cambian el stack, §5): añadir, quitar o mover ACOs o fichas entre sprints; nuevas dependencias, componentes o cambios de stack; cambios de seguridad o privacidad (whitelist, JWT, secretos, persistencia de documentos, retención, prompt injection, datos reales); cambios en los contratos de API entre áreas; reasignaciones; reestimaciones de más del 50%; cambios que afecten a lo acordado con ACANPAN; y las cuestiones abiertas de arquitectura. *(Plan de Trabajo §8; §4 para las dependencias nombradas)*
- **Puede decidirlos la persona responsable, informando en la PR:** refactors internos del ACO, corrección de bugs, ampliación de tests y documentación, dividir el ACO en Issues sin cambiar su alcance y ajustes menores de estimación. *(Plan de Trabajo §8)* El agente puede proponerlos en la PR, y la decisión es de la persona responsable.
- **Hace falta ADR** si la decisión es difícil de revertir, afecta a la seguridad, la privacidad o los datos de pacientes, añade, retira o sustituye una dependencia o un componente del stack, afecta a más de un área o se aparta del Plan de Proyecto o de la Arquitectura. Un ADR aprobado no se edita: se sustituye por otro. *(Plan de Trabajo §9)*

## 8. Seguridad y datos

- No se desactivan controles de seguridad para facilitar una prueba. *(Plan de Trabajo §4)*
- Las credenciales y los secretos nunca se almacenan en Git. *(Plan de Trabajo §10)*
- Las pruebas usan documentos sintéticos y los documentos originales de pacientes no se persisten. *(Plan de Trabajo §10)*
- El detalle de las reglas de privacidad y seguridad está en `docs/arnes/03-REGLAS.md`.

## 9. Flujo de Git y PR

*(Plan de Trabajo §4)*

- Flujo: Issue → rama → desarrollo local → tests → Pull Request → revisión de la otra persona → CI verde → merge. **Ningún cambio directo sobre main.**
- Ramas: `feature/ACO-XXX-descripcion` o `fix/ACO-XXX-descripcion`.
- La Issue es solo un puntero (título, responsable, estado y enlace a la ficha). La PR enlaza su ficha y su Issue y se revisa con la Guía rápida de revisión de PR.
- El primer commit de la PR es la ampliación de la ficha (§3). La descripción de la PR recoge las decisiones delegadas que se han tomado (§5) y las cuatro categorías (§6).
- El revisor aprueba o rechaza según el contenido, sin modificarlo; los cambios los aplica el autor. El merge lo hace el revisor al aprobar, con la CI en verde, salvo que el autor pida en la PR que se espere.
- Merge **siempre squash**. Título del commit: el de la PR, que empieza por el ID del ACO o del ADR («ACO-021: Presidio + MEDDOCAN»), con un cuerpo breve y sin el listado de commits intermedios.
- **Coautoría con IA:** si ha intervenido un agente, el commit final lleva **una sola** línea `Co-Authored-By` del agente.

## 10. Definition of Done

*(Plan de Trabajo §10)*

- Criterios de aceptación de la ficha cumplidos.
- Código implementado y revisado.
- Tests correspondientes ejecutados y CI verde.
- Documentación actualizada cuando corresponda.
- Sin secretos ni datos reales de pacientes.
- Integraciones afectadas comprobadas.
- PR enlazada a su ficha e Issue.

El sprint en curso puede añadir criterios en su Documento Operativo (ver `docs/arnes/08-PLAN.md`).

## 11. El arnés

*(Estrategia §4.1)*

- El arnés **no se edita a mano** dentro de un ACO: se regenera desde las fuentes. Si el agente detecta un error en el arnés, lo informa; la corrección se hace en la fuente oficial y después se regenera.
- Ningún documento oficial ni ADR cita archivos del arnés: el agente no añade esas referencias.
- El Calendario de Acciones no es fuente.
