# ADR-028 — Clasificador de intención previo a la llamada al LLM

Estado: aprobado

Sustituido por: —

Origen: Decisión conjunta #169 (opción C, cerrada el 18 nov 2026), que sitúa el clasificador en el Sprint 2, en el bloque «límites del LLM», y encarga este ADR antes del BUILD y antes del 25 nov 2026. Lo implementa ACO-042 (bloque «límites del LLM», ACO-035–046). Las acciones posteriores al merge (registro del Plan de Trabajo §9, retirada de la cuestión de la Arquitectura, UC-08, regeneración del arnés y fila de ACO-042 en la matriz del Documento Operativo) tienen vehículo en la Issue #207. Cierra la cuestión 1 de la Arquitectura v0.10 §16 («el clasificador de intención ya tiene módulo asignado —el LLM gateway—, pero falta decidir en qué sprint se implementa»).

Relacionados: ADR-006 (LLM gateway obligatorio), ADR-008 (sin datos reales hasta salvaguardas), ADR-015 (secretos), ADR-019 (E2E con gateway simulado), ADR-024 (registro de auditoría); ACO-027 (gateway), ACO-029 (prompt de sistema), ACO-030 (conversación), ACO-041 (prompt v1 e historial manipulado), ACO-042 (implementación), ACO-052 (catálogo de casos); #145 y #170 (conversación sin documento), #116 (respuesta inyectada en el historial), #87 (decisión del modelo principal y su razonamiento), #92 (clave del proyecto y límite de gasto), #172 (caché de prompts).

## Contexto

Hoy la conversación llama al gateway directamente (`ConversationService.answer` → `LLMGateway.complete`). Lo único que mantiene al modelo en su ámbito es el prompt de sistema de ACO-029 (R-25): «Solo atiendes cuestiones relacionadas con la documentación clínica del paciente, con el cáncer de páncreas y con su proceso oncológico». La sonda S4 de ACO-029 y el catálogo de ACO-052 muestran que el prompt declina las preguntas fuera de ámbito, pero es una sola barrera y depende de que el modelo la respete en cada respuesta.

Las fuentes piden una segunda:

- **Arquitectura §1:** los controles de uso oncológico del modelo —clasificador de intención y control de gasto— son necesarios desde el inicio.
- **Arquitectura §11:** el clasificador es previo a la llamada al LLM y se integra en el LLM gateway.
- **ADR-006:** el gateway es el punto único que integra el control de gasto y el clasificador de intención. El propio `gateway.py` deja anotado que el clasificador se añadirá ahí después del Sprint 1.
- **UC-08:** antes de enviar la pregunta al LLM se valida que es relevante para el ámbito oncológico.

Condiciones que fija #169 y que este ADR respeta:

- **No es criterio de la demo de diciembre.** Si en la revisión de mitad de sprint (#168, 4 dic) el ACO llega en rojo, se aplica el recorte de #144 y la demo va con el prompt como única barrera, con la desviación registrada.
- **Los topes de gasto van en el Sprint 3.** Hasta entonces el tope provisional es el límite de la consola de la clave del proyecto (#92).
- **La conversación sin documento (#170) no se abre hasta que existan el clasificador y los topes.**

Restricciones que ya están en vigor:

- R-23: toda llamada a Claude API pasa por el gateway.
- R-04: ni el contenido de los documentos ni el nombre de su fichero aparecen en logs.
- El contrato de `POST /api/conversation` (ACO-030) es público y lo consume el frontend (ACO-032).
- El prompt de ACO-029 no se toca en este ADR.

## Decisión

1. **Qué clasifica.** Antes de la llamada principal, el clasificador asigna al **último mensaje del paciente** una de dos etiquetas: `en_ambito` o `fuera_de_ambito`.
   - `en_ambito` incluye todo lo que el prompt de ACO-029 atiende: el documento, el cáncer de páncreas y su proceso, términos, pruebas, tratamientos mencionados, preparación de la consulta, y también las **preguntas sobre síntomas o urgencias** (sonda S8), que deben llegar al modelo para que remita al equipo o al 112.
   - `fuera_de_ambito` es solo lo **claramente ajeno**: tareas generales, entretenimiento, opiniones, temas sin relación con su proceso oncológico.
   - **La duda se resuelve como `en_ambito`.** Un falso positivo —bloquear una pregunta oncológica legítima— es peor para el paciente que un falso negativo, que el prompt sigue declinando. El clasificador recorta lo evidente; el prompt sigue siendo la barrera de fondo.

2. **Qué recibe.** Solo el texto del último mensaje del paciente y un indicador de si hay conversación previa. **No recibe los documentos** ni el historial.
   - Sin documentos: el texto de un documento no cambia si la pregunta es de ámbito, y enviarlo multiplicaría el coste de cada clasificación.
   - Sin historial: los mensajes previos los envía el cliente y pueden estar manipulados (#116).
   - Con el indicador: un seguimiento corto en una conversación en curso («¿y eso es grave?», «explícamelo otra vez») se clasifica `en_ambito`.
   - **De dónde sale el indicador.** Es un booleano que el backend deriva de si el historial que envía el cliente está vacío; no se lee su contenido ni se envía al clasificador. Un cliente que lo falsee solo relaja la clasificación de un mensaje suelto, y el prompt de ACO-029 sigue siendo la barrera de fondo.

3. **Cómo clasifica.** Con una llamada a **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) a través del gateway, con un prompt de clasificación propio, **temperatura 0** y una salida de una sola etiqueta.
   - **Proveedor.** No añade un encargado de tratamiento: el mensaje va al mismo proveedor que ya trata los mensajes del paciente. Si la pregunta está en ámbito, también va a la llamada principal; si se bloquea, la clasificación es el único envío y se ahorra la llamada principal, no la clasificación.
   - **Prompt.** Es un fichero versionado junto a los de ACO-029 (`app/services/prompts`), con su huella en el registro, como el prompt de sistema. **No modifica el prompt de ACO-029.**
   - **Modelo y cambio de modelo.** El modelo es configurable (`LLM_CLASSIFIER_MODEL`), con Claude Haiku 4.5 como valor inicial: es el modelo pequeño de Claude disponible y basta para una salida de una etiqueta. Cambiarlo no exige un ADR nuevo mientras el modelo nuevo cumpla el punto 8: el cambio va en una PR con la evaluación completa repetida y su informe. La decisión del modelo de Claude es la del modelo principal, no la del clasificador: #87 espera ese ADR y no es él.
   - **Salida y tiempo.** Límite de salida de pocas decenas de tokens, sin razonamiento extendido, y tiempo máximo propio (`LLM_CLASSIFIER_TIMEOUT_SECONDS`), más corto que el de la llamada principal. Los valores iniciales de estas dos variables los fija la ficha de ACO-042.
   - **Salida no reconocible.** Una respuesta que no sea exactamente una de las dos etiquetas se trata como `en_ambito`.

4. **Si el clasificador falla, la conversación sigue (fail-open).** Si la clasificación agota su tiempo, devuelve un error del proveedor o una salida no reconocible, la petición continúa a la llamada principal con el prompt como barrera, y el gateway registra `intent_check_failed` con el motivo.
   - Bloquear ante un fallo convertiría una incidencia puntual del proveedor en una denegación del servicio para el paciente, cuando la llamada principal depende del mismo proveedor y el prompt sigue activo.
   - La tasa de fallos se vigila en el registro. Si en el piloto supera lo razonable, se revisa este punto.

5. **Si la pregunta es `fuera_de_ambito`, no hay llamada principal.** La conversación devuelve una respuesta fija, con el mismo formato de siempre: `answer` con un texto que declina con amabilidad y recuerda para qué sirve ACOMPAS, y `truncated` en falso.
   - **El contrato de `POST /api/conversation` no cambia**: ningún campo nuevo, ningún código de error nuevo. El frontend muestra la respuesta como cualquier otra, con el disclaimer visible.
   - El literal lo fija la ficha de ACO-042 y repite la idea de la sección «Ámbito» del prompt de ACO-029: qué sí puede hacer ACOMPAS.

6. **Dónde vive: dentro del gateway, sin depender del llamante.** El gateway ofrece una **operación de conversación** que clasifica dentro y, si la pregunta pasa, llama al modelo principal. La conversación usa esa operación; `complete()` deja de ser su entrada y queda como vía interna del gateway, que la clasificación usa sin clasificarse a sí misma.
   - Así se cumple ADR-006: el clasificador se aplica de forma uniforme en un único punto, y ninguna conversación puede llegar al modelo principal sin pasar por él, aunque el llamante se olvide.
   - Un test comprueba que la ruta de conversación no tiene otra entrada al modelo principal.
   - La interfaz concreta (nombre, firma y modelos de datos) la fija la ficha de ACO-042.

7. **Qué se registra.** Solo metadatos, como hoy en `llm_call`: etiqueta, modelo, tokens de entrada y salida, duración, huella del prompt de clasificación y, si falla, el motivo. **Nunca el texto del mensaje del paciente.** Es una regla nueva: R-04 cubre el contenido del documento y el nombre de su fichero, no los mensajes, y 03-REGLAS la amplía a los mensajes del paciente.
   - Los tokens de la clasificación son gasto del paciente: los topes del Sprint 3 los cuentan junto a los de la llamada principal.

8. **Cómo se acepta.** ACO-042 incluye un conjunto de evaluación sintético y etiquetado, y una ejecución real opcional (`ACOMPAS_LLM_LIVE=1`), con el mismo patrón que el ejecutor de ACO-052. Con temperatura 0, el conjunto completo se ejecuta **tres veces** y los criterios se cumplen en las tres, para no aceptar un resultado que dependa de una pasada afortunada.
   - **En ámbito:** los mensajes C01–C05, C07–C13 y C15 del catálogo de ACO-052 y las sondas S1–S3 y S5–S9 de ACO-029, más al menos 20 preguntas límite que deben pasar: nutrición durante el tratamiento, ansiedad por el diagnóstico, efectos secundarios, trámites de la consulta, síntomas urgentes, seguimientos cortos en conversación.
   - **Fuera de ámbito:** C06 del catálogo y la sonda S4 —la petición de un poema, que el punto 1 define como «fuera de ámbito»—, más al menos 20 peticiones claramente ajenas.
   - **C14 y los casos de interfaz** quedan fuera de los dos conjuntos: no son una entrada del clasificador, sino la pregunta de C01 en modo `demo`.
   - **Criterio:** **ningún falso positivo** en el conjunto en ámbito, en ninguna de las tres ejecuciones, y al menos el 80 % de detección en el conjunto fuera de ámbito en cada una. Lo que se escapa lo sigue declinando el prompt.
   - El informe registra modelo, huella de los dos prompts, tasa de fallos y latencia y tokens medios de la clasificación.

9. **Pruebas sin red.** Los tests unitarios usan un clasificador falso inyectable, igual que el proveedor falso del gateway. El E2E de ADR-019 sustituye el gateway completo por uno simulado, que no clasifica; la conversación con y sin bloqueo se prueba en los tests del backend.

## Alternativas consideradas

- **Solo el prompt (situación actual).** Descartada: la Arquitectura §1 y §11 y UC-08 piden un control previo a la llamada.
- **Reglas o palabras clave.** Descartada: en español y con lenguaje coloquial, una lista se queda corta y produce falsos positivos con términos médicos y con preguntas legítimas formuladas de forma inesperada.
- **Clasificador local con sentence-transformers** (está en el stack, R-32, sin coste por llamada y sin salida de datos). Descartada por ahora: necesita un corpus etiquetado y una calibración que no existen, añade un modelo a la imagen (#159) y rinde peor en preguntas matizadas. Se reconsidera cuando el piloto aporte datos reales etiquetables, siempre anonimizados.
- **Clasificar dentro de la llamada principal** (pedir al modelo una etiqueta antes de la respuesta). Descartada: no es «previo a la llamada», el modelo ya habría recibido los documentos y no ahorra coste.
- **Bloquear ante un fallo del clasificador (fail-closed).** Descartada por el punto 4: una incidencia del proveedor dejaría sin servicio al paciente sin ganar protección, porque el prompt sigue activo.
- **Enviar los documentos o el historial al clasificador.** Descartada por el punto 2: más coste y más exposición, sin mejorar la decisión, y el historial lo controla el cliente.
- **Servicio de moderación de terceros.** Descartada: añade un encargado de tratamiento y no conoce el ámbito oncológico de ACOMPAS.
- **Devolver un código de error o un campo nuevo al bloquear.** Descartada: cambiaría el contrato público de ACO-030 y obligaría a tocar el frontend, sin beneficio para el paciente.

## Consecuencias

- Cada mensaje del paciente cuesta una llamada corta adicional al proveedor. La latencia y los tokens se miden en ACO-042; la caché de prompts (#172) no se aplica a esta llamada.
- Las preguntas claramente ajenas dejan de llegar al modelo principal: menos coste y menos superficie para sacar al modelo de su ámbito.
- Variables de entorno nuevas: `LLM_CLASSIFIER_MODEL` y `LLM_CLASSIFIER_TIMEOUT_SECONDS`, con su documentación en `.env.example` y el README. No hay secretos nuevos: usa la misma clave (ADR-015).
- Un prompt nuevo, versionado y con huella. El prompt de ACO-029 no cambia.
- La conversación entra al modelo principal solo por la operación de conversación del gateway; `complete()` queda como vía interna.
- El contrato de `POST /api/conversation` no cambia.
- El arnés gana una regla (clasificación previa obligatoria en la conversación, con la duda a favor del paciente) y su verificación, y R-04 se amplía a los mensajes del paciente.
- Estimación de ACO-042: **8–10 h**, la de la matriz del Documento Operativo del S2 (módulo, prompt, integración, tests, conjunto de evaluación y ejecuciones reales).
- **La conversación sin documento (#170)** queda con una de sus dos dependencias cubierta; le sigue faltando la de los topes (S3).

## Fuera de esta decisión

- Los topes de gasto y la regla de cálculo del crédito (Arquitectura §16 nº 16; Sprint 3).
- La elección y la política de versiones del modelo principal de Claude, incluido el razonamiento (decisión del modelo; #87).
- El control de prompt injection y la respuesta inyectada en el historial (#116, ACO-041): el clasificador decide el ámbito, no detecta ataques.
- El registro de auditoría: la clasificación no es un evento de ADR-024; deja solo los metadatos del punto 7 en el registro del gateway.
- La conversación sin documento y su marcador (#170).
- El literal de la respuesta al bloquear y los valores iniciales del límite de salida y del tiempo máximo: ficha de ACO-042.

## Documentos afectados

- Arquitectura del Sistema §11 y §16 (cierra la cuestión 1).
- Casos de Uso UC-08 (validación de ámbito antes de enviar la pregunta).
- Arnés: 03-REGLAS (regla nueva de clasificación y ampliación de R-04 a los mensajes del paciente), 05-DISEÑO, 07-INTERCAMBIO y 09-TESTS (verificación nueva), en la siguiente regeneración.
- Plan de Trabajo §9 (registro de ADR).
- Ficha de ACO-042 y su fila en la matriz del Documento Operativo del Sprint 2 (§6).
- `.env.example` y README (variables nuevas), con ACO-042.
