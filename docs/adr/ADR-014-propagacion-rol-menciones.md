# ADR-014 — Propagación del rol entre menciones de la misma persona
Estado: aprobado

Sustituido por: —

Origen: Decisión conjunta #65 (aprobada sin objeciones, 12/10/2026); cuestión 7 de la Arquitectura §16

Relacionados: ADR-005, ADR-012, ADR-013

## Contexto
ADR-012 numera las etiquetas por documento y deja abierta la agrupación de las variantes de un nombre. ADR-013 toma el rol de la etiqueta del modelo, reforzada por pistas de contexto, y usa la etiqueta genérica de persona cuando el rol no está claro. Por eso una mención sin pista puede conservar el rol del modelo o quedar como persona genérica aunque el documento ya haya identificado a esa persona en otra mención. ACO-023 necesita que todas las menciones de una persona compartan número. Este ADR no sustituye a ADR-012 ni a ADR-013: cierra la cuestión que ambos dejaron abierta.

## Decisión
1. La agrupación es siempre dentro de un documento, nunca entre documentos.
2. Se consideran el mismo nombre las mismas palabras, sin contar orden, mayúsculas, tildes ni puntuación. Para comparar se ignoran los tratamientos, pero la pista de rol se evalúa antes de quitarlos: un tratamiento que indique rol sigue siendo pista.
3. El rol solo se propaga desde una mención con pista, conforme a ADR-013. No se propaga el rol que el modelo asigna sin pista.
4. Una mención parcial hereda el rol si tiene al menos dos palabras tras quitar los tratamientos, todas sus palabras están contenidas en el nombre completo de una persona con pista y no encaja con otra persona de rol distinto.
5. Una palabra suelta nunca hereda. Una mención más larga que el nombre con pista, aunque lo contenga, tampoco hereda.
6. Una mención con pista propia conserva su rol.
7. El rol propagado prevalece sobre el rol del modelo, porque prevalece el contexto (ADR-013).
8. Si la mención encaja con dos o más personas con roles distintos, no se propaga y queda como persona genérica, aunque el modelo le hubiera asignado un rol. Si los roles coinciden, se propaga. Con pistas contradictorias, cada mención con pista conserva la suya.
9. La propagación solo cambia la etiqueta de menciones ya detectadas: no detecta nombres nuevos, no fusiona hallazgos y no cambia posiciones ni puntuaciones.
10. No se guardan nombres ni valores originales. La agrupación es en memoria y no se escribe en logs, errores ni avisos (ADR-005, ADR-012).
11. No se añaden pistas de familiar: ese rol sigue dependiendo del modelo.

## Alternativas consideradas
- No propagar: descartada; el LLM pierde la identidad y ACO-023 no puede numerar de forma coherente.
- Propagar también el rol del modelo sin pista: descartada; es menos fiable que una pista.
- Propagar a nombres de una palabra: descartada; la ambigüedad es demasiado alta.
- Propagar entre documentos: descartada; contradice la numeración por documento y la privacidad.
- Ignorar las pistas contradictorias: descartada; la pista es la evidencia más fuerte.
- No propagar nunca en caso ambiguo con roles coincidentes: descartada; se pierde información segura.
- Entity linking o embeddings: descartada; añade complejidad y dependencias sin necesidad.
- Guardar nombres normalizados: descartada; no se persiste ningún dato del documento.
- Fusionar las menciones en un solo hallazgo: descartada; la anonimización necesita cada aparición.

## Consecuencias
- La ficha de ACO-022 recoge la regla y sus casos de prueba; ACO-023 usa la misma agrupación para numerar; ACO-026 incorpora los casos.
- El acierto de rol sigue siendo un indicador de calidad, sin bloquear. Un rol mal propagado no es una fuga: afecta a la comprensión, no a la privacidad.
- La confianza del documento no cambia: las etiquetas de persona cuentan como una sola categoría (ADR-013).
- Los casos ambiguos quedan conservadoramente como persona genérica.
- Dos personas distintas con el mismo nombre normalizado pueden agruparse.

## Fuera de esta decisión
- Coherencia entre documentos.
- Algoritmo de normalización y estructuras de datos.
- Formato y secuencia de la numeración (ACO-023).
- Nuevas pistas de rol, incluidas las de familiar.
- Detección de nombres nuevos, entity linking o embeddings.
- Texto de los avisos y del prompt.
- Cambios en la política de anonimización o en los umbrales.

## Documentos afectados
Arquitectura del Sistema (§16, cuestión 7), Plan de Trabajo (registro de ADR), fichas ACO-022, ACO-023 y ACO-026 (al ampliarlas) y Documento Operativo si cambia alguna estimación.
