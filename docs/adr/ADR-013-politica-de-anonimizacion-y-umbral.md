# ADR-013 — Política de anonimización del Nivel 1: qué se anonimiza, umbrales y documento retenido
Estado: aprobado  
Sustituido por: —  
Origen: ADR pendiente del Plan de Trabajo §9 (umbral de confianza, ACO-023); calibración de ACO-021 y lecciones de un anonimizador previo con Presidio + MEDDOCAN, 8 de octubre de 2026  
Relacionados: ADR-001, ADR-003, ADR-005, ADR-008, ADR-012  

## Contexto
ADR-003 fija la anonimización en tres niveles y deja fuera el valor del umbral, el objetivo de cobertura y las reglas concretas de Presidio. El Plan de Trabajo §9 tiene pendiente el umbral de confianza y el tratamiento del documento retenido, que necesita ACO-023.
Al preparar ACO-022 y ACO-023 han aparecido tres cosas más que tampoco están decididas:
- La Arquitectura §4 enumera lo que detecta Presidio («nombres, fechas, direcciones…») y usa etiquetas por rol ([PACIENTE], [MÉDICO_1], [HOSPITAL], [FECHA_NACIMIENTO]), pero no dice qué fechas se anonimizan ni qué pasa con edad, sexo, profesión o localidad.
- El código de ACO-021 en main agrupa paciente, sanitarios y familiares en un único tipo de persona, con lo que se pierden las etiquetas por rol.
- El modelo MEDDOCAN devuelve muchas detecciones de puntuación baja que no son datos personales, y a veces detecta solo una parte de un nombre o una dirección. Un único umbral no sirve a la vez para descartar ese ruido y para decidir si un documento es fiable.
Además, UC-06, el wireframe 4 y el Modelo E/R hablan de revisar «después» el documento retenido, lo que choca con que el original no se persiste (ADR-005).
El documento anonimizado sigue siendo un dato personal seudonimizado: la base de datos de ACOMPAS solo guarda el UUID del paciente y la correspondencia con su email la custodia Keycloak (ADR-001). Si se comprometiera solo la base de datos, la única vía de reidentificación sería el contenido del documento, de ahí la importancia de lo que se anonimiza.

## Decisión
**Se anonimiza siempre** (categorías garantizadas):
- Nombres de personas, sea cual sea su rol.
- Identificadores: DNI, NIE, número de historia clínica, tarjeta sanitaria y otros identificadores de aseguramiento, de episodio asistencial y del personal sanitario (empleo y colegiación).
- Teléfono, fax y correo electrónico.
- Dirección: vía, número, piso, código postal y localidad.
- Fecha de nacimiento.

**Se anonimiza si se detecta, sin garantía:** hospital, centro de salud e institución. Se sustituyen por su etiqueta cuando el modelo los detecta, pero no cuentan para la confianza del documento ni para las comprobaciones de fuga.

**Rol de las personas, sin garantía:** la etiqueta indica el rol (paciente, personal sanitario, familiar) cuando se puede determinar. El rol se toma de la etiqueta del modelo, reforzada por pistas de contexto («Dr.», «Dra.», «Solicitante:» o la firma fechada indican personal sanitario; «Paciente:», paciente). Si el modelo y el contexto se contradicen, prevalece el contexto. Si el rol no está claro, se usa una etiqueta genérica de persona numerada, en lugar de un rol que puede ser erróneo.

**No se anonimiza**, porque es contexto clínico que el paciente necesita y por sí solo no lo identifica: las demás fechas del documento (informe, extracción, consulta), la edad, el sexo, la profesión y el país.

**Ante la duda, se anonimiza.** La única excepción es cuando tachar oculta el propio contenido clínico (nombres de pruebas, resultados, variantes genéticas); para eso están los filtros de falsos positivos.

**Dos umbrales distintos**, ambos configurables:
- *Umbral de hallazgo* (valor inicial 0,35): por debajo, la detección se descarta como ruido. Todo lo que lo supera y pasa los filtros se anonimiza, aunque su puntuación no sea alta.
- *Umbral de documento* (valor inicial 0,85): si la confianza del documento queda por debajo de este umbral, el documento se retiene. La confianza del documento mide si los datos personales de categorías garantizadas se han detectado bien. No la rebajan la duda sobre el rol de una persona (las etiquetas de persona cuentan como una sola categoría) ni las categorías sin garantía. Un documento sin ninguna entidad de categorías garantizadas tiene confianza máxima: no hay nada que anonimizar (por ejemplo, una dieta).

**Documento retenido:** no se carga ni pasa a la conversación, y no se guarda ni el original ni el resultado anonimizado. Se informa al paciente de que el documento no se ha podido procesar con garantías y puede intentarlo con otra copia. Solo queda un registro para auditoría, sin contenido ni nombre del fichero (fecha, tipo de documento, motivo).

**Documento ilegible:** si el texto extraído está vacío, el documento no se procesa y se avisa al paciente con ese motivo, distinto del de baja confianza.

## Alternativas consideradas
- Un solo umbral por hallazgo, sin retener documentos: descartada; ADR-003 exige retener los documentos de baja confianza.
- Un solo umbral para todo: descartada; un valor alto deja sin anonimizar detecciones dudosas, y uno bajo hace que la confianza del documento no signifique nada.
- No anonimizar las detecciones entre los dos umbrales: descartada; serían fugas de datos.
- Anonimizar todas las fechas: descartada; se pierde la cronología clínica, que es necesaria para entender el documento.
- Anonimizar el hospital con garantía: descartada; es difícil de detectar (aparece repartido en varias líneas, abreviado o con nombre de persona) y retendría documentos por un dato de poco riesgo.
- No anonimizar el hospital, con una lista de hospitales permitidos: descartada; con pacientes de toda España la lista no tiene fin, un hospital con nombre de persona que no esté en ella se anonimizaría igualmente como persona, y la Arquitectura §4 ya incluye el hospital.
- Una sola etiqueta para todas las personas: descartada; el LLM y el paciente necesitan distinguir al paciente de sus médicos.
- Garantizar el rol de cada persona: descartada; el modelo se equivoca de rol en listas, cabeceras sin etiqueta y nombres sueltos, y un rol erróneo confunde más al LLM que una etiqueta neutra.
- Fijar en este ADR la fórmula de la confianza del documento, por ejemplo la puntuación más baja de sus entidades: descartada. La puntuación del modelo mide el tipo concreto de entidad, así que un nombre detectado sin duda pero con rol dudoso, o troceado en subpalabras, saca una puntuación baja y retendría documentos sin riesgo real. La fórmula se fija al calibrar.
- Retener los documentos sin ninguna entidad detectada: descartada; hay documentos legítimos sin datos personales, como una dieta.
- Conservar el documento retenido para revisarlo después: descartada; obligaría a persistir el original, contra ADR-005.

## Consecuencias
- ACO-022 corrige el mapeo de ACO-021 para conservar el rol, añade la asignación de rol por contexto con la etiqueta genérica como caída, y añade los reconocedores propios (DNI y NIE con letra de control, número de historia por contexto, nombres tras etiqueta, dirección completa, firmas).
- ACO-023 define y documenta la fórmula de la confianza del documento, calibrada con el corpus de ACO-051 y con el criterio de esta decisión. Para que la duda de rol no la rebaje, tiene que usar las probabilidades de todas las etiquetas de persona del modelo, no solo la ganadora que devuelve Presidio por defecto.
- ACO-023 implementa los dos umbrales, la confianza del documento, los filtros de falsos positivos, la retención y el aviso de documento ilegible. Los tests no fijan valores: los leen de la configuración.
- Las comprobaciones de fuga (corpus sintético de ACO-051, T-31 del arnés) cubren solo las categorías garantizadas y comprueban que el dato ha desaparecido, no el rol asignado. El acierto de rol se mide como indicador de calidad, sin bloquear, con casos sintéticos definidos en la ficha de ACO-022.
- Un rol erróneo no es una fuga: el nombre se sustituye igualmente. Su efecto es de comprensión, porque el LLM puede atribuir a una persona lo que hizo otra.
- La Arquitectura y los wireframes mantienen las etiquetas por rol ([PACIENTE], [MÉDICO_1]); hay que añadir la etiqueta genérica de persona.
- Los valores iniciales de los umbrales y la fórmula se calibran con el corpus sintético de ACO-051. Cambiarlos no requiere un ADR nuevo mientras se respete el criterio de esta decisión; el cambio y su justificación quedan en la PR que lo hace.
- Se sobre-anonimizan algunos datos institucionales (por ejemplo, la dirección del hospital en la cabecera), a cambio de no dejar pasar datos del paciente.
- El nombre de un hospital puede escaparse, o anonimizarse como persona si lleva nombre de persona.
- Se acepta que un documento con datos personales en el que la detección falle por completo pase como documento sin entidades. Es poco probable y la revisión del paciente (Nivel 3) actúa como red de seguridad.
- Un documento retenido se pierde para ACOMPAS: el paciente tiene que volver a subirlo.
- Descartar el documento retenido es el comportamiento mientras no exista el Nivel 3. Está previsto que el Nivel 3 haga la revisión del paciente en el momento de la carga, antes de guardar nada y de cualquier envío a Claude. Entonces el documento retenido pasará a revisión obligatoria en lugar de descartarse.

## Fuera de esta decisión
- Lista concreta de reconocedores, filtros y términos permitidos: fichas de ACO-022 y ACO-023.
- Texto de los avisos al paciente (documento retenido e ilegible).
- Nombre exacto de la etiqueta genérica de persona y del catálogo de etiquetas (Modelo E/R, TIPO_ETIQUETA).
- Comprobar que el documento es de tipo clínico antes de procesarlo (por ejemplo, una multa subida por error, con datos como la matrícula que el anonimizador no conoce).
- Uso de la confianza del OCR para detectar documentos ilegibles, y si cambian los umbrales en los Niveles 2 y 3 o al usar documentos reales.
- Diseño del Nivel 3: marcado de datos que se han escapado y ocultación de contenido por decisión del paciente en el momento de la carga, almacenamiento temporal durante la revisión y marcado posterior a la carga.
- Cómo se agrupan las variantes de un mismo nombre dentro de un documento (ADR-012).

## Documentos afectados
Arquitectura del Sistema, Modelo E/R, Casos de Uso, Wireframes, Plan de Trabajo (registro de ADR), Documento Operativo Sprint 1 (estimaciones, si cambian), fichas ACO-022, ACO-023 y ACO-026 (al ampliarlas).
