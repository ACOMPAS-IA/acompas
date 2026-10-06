# ADR-012 — Qué se conserva de cada documento original
Estado: aprobado  
Sustituido por: —  
Origen: Revisión del Modelo E/R, 6 de octubre de 2026  
Relacionados: ADR-001, ADR-003, ADR-005  

## Contexto
ADR-005 establece que el documento original no se persiste. Sin embargo, el Modelo E/R v0.7 conserva datos derivados que permiten reconstruirlo o identificar al paciente: ETIQUETA_ANONIMIZACION.valor_original guarda cifrado cada dato identificativo junto con su posición en el texto, y DOCUMENTO.nombre_original guarda el nombre del fichero, que puede contener el nombre del paciente.
valor_original se usaba para que una persona tuviera siempre la misma etiqueta en todos los documentos del paciente (por ejemplo, que [MÉDICO_1] fuera siempre el mismo médico).

## Decisión
- Las etiquetas de anonimización se numeran por documento: [MÉDICO_1] en un documento no tiene relación con [MÉDICO_1] en otro. No se mantiene coherencia entre documentos.
- No se guarda el valor original de ninguna entidad detectada, ni cifrado ni de ninguna otra forma.
- El documento no conserva el nombre del fichero original; se guarda un nombre genérico formado por el tipo de documento y la fecha de carga.
- Se guarda un hash criptográfico del fichero original, único por paciente, para detectar subidas repetidas del mismo fichero. Ante un duplicado se avisa al paciente en lugar de procesarlo de nuevo; si el paciente borró antes el documento, puede volver a subirlo.

## Alternativas consideradas
- Coherencia entre documentos con valor_original cifrado: descartada. Las variantes de un mismo nombre (solo apellido, apellido y nombre, nombre y apellido) no se resuelven de forma fiable, y fusionar por error a dos médicos distintos es clínicamente peligroso. La comparación exige descifrar en tiempo de ejecución, así que la clave tiene que estar en el servidor de la aplicación. Además, con los valores y sus posiciones se puede reconstruir el documento original.
- Coherencia por paciente mediante un hash con clave del valor normalizado: descartada. Hereda el problema de las variantes, y con valores poco variados (apellidos, fechas) es atacable si se filtra la clave.
- Que el paciente ponga nombre a sus etiquetas (por ejemplo, «[MÉDICO_1] es mi oncólogo»): aplazada. Se valorará si en las pruebas con documentos reales se echa en falta la coherencia entre documentos.
- Hash del texto anonimizado para detectar duplicados: descartada. El OCR no es estable entre escaneos y la comprobación llegaría después de procesar el documento.
- Unicidad del hash entre todos los pacientes: descartada, porque permitiría saber si dos pacientes subieron el mismo documento.

## Consecuencias
- Ningún dato del sistema permite reconstruir el documento original, en línea con ADR-005.
- El LLM no puede saber si dos documentos mencionan a la misma persona; el paciente sí lo sabe y puede aclararlo en la conversación.
- TIPO_ETIQUETA pasa a ser un catálogo de tipos de etiqueta, sin numeración global.
- Solo se detectan duplicados exactos: una nueva exportación, otro escaneo u otra foto del mismo informe entran como documentos distintos.
- El hash se borra junto con el documento en el derecho al olvido (ADR-001).

## Fuera de esta decisión
- Cómo se agrupan las variantes de un mismo nombre dentro de un documento.
- Algoritmo concreto del hash.
- Texto del aviso de documento duplicado.
- Formato exacto del nombre genérico.

## Documentos afectados
Arquitectura del Sistema, Modelo E/R, Casos de Uso, Wireframes.
