<!--
PLANTILLA DE FICHA ACO EJECUTABLE

Cómo se usa:
1. Toda ficha llega al repositorio como ficha de alcance (objetivo, incluye, fuera de alcance
   y criterio de revisión), acordada entre los dos.
2. Al empezar el ACO, su responsable la amplía con esta plantilla, en la rama y la PR del propio ACO.
3. El alcance acordado se conserva. Lo que se añade y no estaba decidido en ningún sitio
   va en la sección 0 como propuesta, y el revisor lo confirma en la revisión de la PR.
   Lo que ya está decidido en otro sitio (ADR, código existente, contrato de otro ACO)
   se escribe como hecho, citando la fuente.
4. Al aprobarse, la ficha se deja con su estado final: la sección 0 pasa a «Puntos confirmados».

Reglas:
- No repetir responsable, soporte, revisión, estimación ni dependencias: están en la matriz
  operativa del Documento Operativo del sprint en curso, que es su fuente única.
- No citar versiones de documentos.
- Las secciones marcadas como opcionales se eliminan si no aplican.
- Borrar todos estos comentarios al rellenar la ficha.
-->

# ACO-XXX — Nombre del ACO

> **Estado:** criterios de aceptación propuestos por el responsable, pendientes de confirmar en la revisión de la PR.
<!-- Al aprobarse: «criterios de aceptación confirmados en la revisión de la PR #N». -->

## 0. Puntos a confirmar en la revisión

<!-- Elecciones del responsable que no están decididas en ningún documento. Si no hay ninguna, indicarlo. -->

| Nº | Punto | Propuesta | Motivo |
| --- | --- | --- | --- |
| P1 | | | |

## 1. Identificación

- **ID:** ACO-XXX
- **Nombre:**

El responsable, el soporte y la revisión, la estimación y las dependencias de este ACO son los de la matriz operativa del Documento Operativo del sprint en curso, que es su fuente única. Esta ficha no los repite.

## 2. Objetivo

<!-- Copiado de la ficha de alcance. Una o dos frases. -->

## 3. Incluye

<!-- Copiado de la ficha de alcance y, si hace falta, concretado. -->

1.

## 4. Resultado esperado

<!-- Qué debe existir o funcionar al terminar, descrito de forma comprobable. -->

## 5. Fuera de alcance

No forman parte de ACO-XXX:

- 

<!-- Indicar entre paréntesis a qué ACO o sprint corresponde cada exclusión, cuando se sepa. -->

## 6. Relación con otros ACO

Las dependencias de este ACO se consultan en la matriz operativa del Documento Operativo del sprint en curso.

<!-- Aquí solo: qué ACO utilizan su resultado y qué contrato o interfaz les entrega. -->

## 7. Restricciones técnicas

<!-- Ubicación en el repositorio, formatos, interfaces, bibliotecas permitidas.
     Citar los ADR que apliquen (por ejemplo ADR-004, ADR-006, ADR-008). -->

### Ubicación

```
ruta/del/componente/
```

## 8. Secciones específicas del ACO (opcional)

<!-- Las que necesite el ACO: formato de datos, contenido, reglas de negocio, etc.
     Renombrar y numerar según convenga. Eliminar si no aplica. -->

## 9. Datos de prueba

Está prohibido utilizar datos reales de pacientes, también como punto de partida (ADR-008).

<!-- Indicar qué datos sintéticos se usan, por ejemplo los de ACO-051. -->

## 10. Criterios de aceptación

### AC-01 — Título

Descripción comprobable.

### AC-02 — Alcance

El PR solo modifica los componentes de la sección 12.

## 11. Tests esperados

Como mínimo:

1. 

<!-- Indicar si deben pasar sin red, sin modelos o sin servicios externos. -->

## 12. Componentes esperados

La implementación debe limitarse a:

- `ruta/del/componente/`;
- `docs/aco/ACO-XXX.md` (esta ficha).

Si hiciera falta modificar cualquier otro archivo, el agente debe detenerse antes de hacerlo.

## 13. Decisiones que requieren BLOQUEO

El agente debe detenerse si necesita:

- usar datos reales;
- añadir o cambiar una dependencia;
- modificar archivos fuera de la sección 12;
- contradecir un ADR o la documentación del proyecto;
- 

## 14. Revisión humana

El revisor debe comprobar:

1. Correspondencia del PR con ACO-XXX.
2. Que los puntos de la sección 0 le parecen correctos.
3. Que el PR no toca nada fuera de la sección 12.
4. Adecuación de los tests.
5. CI verde.

La revisión se realiza contra esta ficha.

## 15. Aclaraciones del responsable (opcional)

<!-- Decisiones que aparecen durante la ejecución y que la ficha no especificaba.
     Se confirman en la revisión de la PR, igual que la sección 0. Eliminar si no hay ninguna. -->

| Nº | Aclaración | Decisión |
| --- | --- | --- |
| B1 | | |
