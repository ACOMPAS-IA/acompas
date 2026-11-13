# 04 — INTERFAZ

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Pantallas, flujos y comportamientos de interfaz que se pueden implementar, con indicación de lo que corresponde al Sprint 1.

## Qué no contiene

- Diseño visual definitivo (colores, tipografía): los wireframes son esquemáticos.
- Textos definitivos de la interfaz, salvo los que fija una fuente.
- Contratos de API: están en 07-INTERCAMBIO.

## Fuentes

- **Normativas:** Plan de Proyecto (§1, §4, §6); Arquitectura del Sistema (§3 Recorrido de una consulta, §4, §6, §7, §8, §9, §11, §14); ADR-012 (nombre genérico y duplicado) y ADR-013 (documento retenido e ilegible).
- **Derivadas:** Casos de Uso (§2, §3); Wireframes MVP (pantallas 1 a 10, incluidas 4b, 4c y la vista móvil); fichas ACO-031 (texto y punto del disclaimer) y ACO-032 (resultado en lenguaje natural y avisos de la pantalla 4). Wireframes y Casos de Uso definen la interacción; ninguno puede contradecir a una fuente normativa *(Estrategia §4.6)*.

## 1. Flujo del Sprint 1 (interfaz mínima de la demo)

*(Plan de Proyecto §4, S1; Arquitectura §3, §14 fila S1; UC-01, UC-03, UC-04, UC-05, UC-06, UC-08)*

Login con 2FA (Keycloak), sin barra de disclaimer → acceso solo si el email está en la lista blanca → subida de un documento oncológico **sintético** (aviso de duplicado si el hash coincide con uno ya subido) → anonimización de Nivel 1 con validación automática (umbral de hallazgo y umbral de documento) → resultado en lenguaje natural → pregunta sobre el documento → respuesta de Claude con el disclaimer visible.

- Si la confianza del documento queda por debajo del umbral de documento, el documento se retiene: no se carga ni se guarda, ni el original ni el resultado anonimizado *(Arquitectura §4)*. La pantalla 4b lo comunica y ofrece intentarlo con otra copia.
- Si el documento es ilegible (texto extraído vacío), no se procesa y se avisa al paciente con un motivo distinto del de baja confianza *(Arquitectura §4)*. La pantalla 4c lo comunica.
- El documento se guarda y se muestra con un **nombre genérico** (tipo de documento y fecha de carga), nunca con el nombre del fichero original *(ADR-012; Arquitectura §9)*.
- La interfaz es **mobile-first**: todas las pantallas se usan a 360 px sin scroll horizontal. La pantalla 10 recoge la vista móvil de las pantallas 1–9 y de los estados 4b y 4c. *(Plan de Proyecto §1, §6; Wireframes 10)*
- Según la Arquitectura §14, en el Sprint 1 no hay historial persistente (S3), Niveles 2 y 3 (S2), RAG (S3+), resumen ni preferencias (S5). Los ACO concretos de la interfaz del Sprint 1, sus exclusiones y los criterios de la demo están en 08-PLAN, y su verificación, en 09-TESTS.

## 2. Pantallas

La columna «Sprint» sale del Plan de Proyecto §4 y de la Arquitectura §14. Cuando una pantalla se reparte entre sprints (3, 4 y 5), qué parte toca al Sprint 1 es una **inferencia** de esas fuentes, no una decisión; el alcance exacto lo fija la ficha del ACO (08-PLAN).

| Nº | Pantalla | Casos de uso | Sprint según la planificación | Comportamiento con fuente |
|---|---|---|---|---|
| 1 | Login | UC-01 | S1 | Usuario o email, contraseña y segundo factor (código de app autenticadora). Autenticación vía Keycloak OIDC; se emite un JWT con expiración; 2FA obligatorio. **No muestra la barra de disclaimer.** *(Wireframes 1 y 10; UC-01; Arquitectura §3, §11; ACO-031 P5)* |
| 2 | Mi panel | UC-17, UC-18, UC-10 | S3 (panel básico) | Lista de conversaciones (título, tema, documentos, última actividad) y documentos cargados, **con su nombre genérico** («Analítica · 12 jun 2026»). Acceso a subir, conversar, resumen, preferencias, solicitar borrado y cerrar sesión. Bloque de consumo: cuando no queda crédito muestra el tope diario agotado, el crédito acumulado a cero y el acceso a «Solicitar desbloqueo»; con crédito disponible muestra el saldo, sin botón. Los documentos se comparten entre todas las sesiones. *(Wireframes 2 y 10; Plan de Proyecto §4; ADR-012; Arquitectura §8)* |
| 3 | Subir documento | UC-04 | S1 (versión mínima) | Selección del fichero, tipo de documento (Informe de patología, Analítica, Carta de oncología, Otro) y aviso de que el documento pasará por anonimización automática y se guardará con un nombre genérico. **Aviso de duplicado:** si el hash del fichero coincide con un documento que el paciente ya tiene, se avisa de que no se ha vuelto a procesar y de que el anterior sigue disponible. «Subir y anonimizar» dispara UC-05, salvo en el duplicado. *(Wireframes 3 y 10; UC-04; ADR-012)* |
| 4 | Validación automática + revisión manual | UC-05, UC-06, UC-20 | S1: resultado de la validación · S2: revisión manual (Nivel 3) | Muestra «Documento validado» y los **datos sustituidos en lenguaje natural**, agrupados por importancia («Tus datos», «Otras personas», «Lugares», «Otros datos identificativos»), **sin confianza, umbral, recuentos ni códigos internos**. La vista del texto anonimizado usa las etiquetas de la Arquitectura §4 (`[PACIENTE]`, `[FECHA_NACIMIENTO]`, `[SANITARIO_1]`, `[HOSPITAL]`, `[PERSONA_1]`). Dos avisos sobre los límites: la etiqueta puede no acertar con el rol de la persona y puede haberse sustituido algún dato clínico, de forma deliberada. En el Nivel 3, el paciente puede seleccionar texto y marcarlo como dato identificativo escapado; es opcional («No he encontrado nada más»). Cada marca se registra en ETIQUETA_ANONIMIZACION. *(Wireframes 4 y 10; UC-20; ACO-032 P8; Arquitectura §4, §9)* |
| 4b | Documento retenido | UC-06 | S1 | «No se ha podido procesar el documento con garantías. Puedes intentarlo con otra copia.» Ofrece volver al panel o subir otra copia. **No muestra texto, ni datos sustituidos, ni los avisos de la pantalla 4.** El documento no se carga, no pasa a la conversación y no se guarda, ni el original ni el resultado anonimizado. *(Wireframes 4b y 10; UC-06; ADR-013; ACO-032 P8)* |
| 4c | Documento ilegible | UC-06 | S1 | «El documento no contiene texto que se pueda leer. Puedes intentarlo con otro fichero.» Motivo distinto del retenido (por ejemplo, una imagen sin OCR). **No muestra texto, ni datos sustituidos, ni los avisos de la pantalla 4.** *(Wireframes 4c y 10; UC-06; ADR-013; ACO-032 P8)* |
| 5 | Conversación | UC-08, UC-09, UC-11 | S1: pregunta y respuesta con disclaimer · S3+: historial, preguntas sugeridas y fuentes RAG | Burbujas de usuario y asistente; cita de la fuente de la respuesta, con el nombre genérico del documento. Barra de **disclaimer permanente** con el literal de ACO-031 P2: «ACOMPAS te ayuda a entender tu documentación, pero no diagnostica ni sustituye al médico. Consulta siempre con tu equipo oncológico.» Aviso de sistema al empezar a consumir el crédito acumulado y al agotarlo; en ese momento se desactiva el campo de pregunta y se ofrece «Solicitar desbloqueo». *(Wireframes 5 y 10; Arquitectura §8, §11; ADR-012; ACO-031 P2)* |
| 6 | Mi resumen | UC-12, UC-13 | S5 | Resumen generado aplicando las preferencias activas, guía de primeros pasos, preguntas sugeridas y exportación a PDF. *(Wireframes 6 y 10; Arquitectura §7)* |
| 7 | Mis preferencias del resumen | UC-21, UC-22 | S5 | Tabla Tipo (Ocultar/Anotar), Campo o sección, Texto, Alcance («Siempre»); editar y eliminar. Las preferencias **no** se crean aquí: se piden en la conversación y la app pide confirmación. Ocultar no afecta al chat. *(Wireframes 7 y 10; Arquitectura §7)* |
| 8 | Solicitar desbloqueo | UC-23 | No fijado | Se ofrece al agotar el tope diario y el crédito acumulado. Campo **«Motivo (opcional)»**, que escribe el paciente y el administrador ve con la solicitud. Muestra el estado «Pendiente de aprobación del administrador» y, al resolverse, el **motivo de la resolución**: obligatorio si se deniega y opcional si se aprueba. *(Wireframes 8 y 10; Arquitectura §8; Modelo E/R SOLICITUD_DESBLOQUEO_CREDITO)* |
| 9 | Admin · Desbloqueos | UC-24 | No fijado | Lista de solicitudes (UUID del paciente, fecha, motivo del paciente, estado) con Aprobar o Denegar y un campo de **motivo de la resolución**, obligatorio al denegar y opcional al aprobar. Cada resolución queda en el historial del paciente con su motivo. El desbloqueo es siempre manual. *(Wireframes 9 y 10; Arquitectura §8; Modelo E/R SOLICITUD_DESBLOQUEO_CREDITO)* |
| 10 | Vista móvil (360 px) | Todas las anteriores | S1 (criterio móvil) y posteriores | Replica las pantallas 1–9 y los estados 4b y 4c a 360 px, sin scroll horizontal. Cada vista mantiene toda la funcionalidad de su pantalla de escritorio. El login no muestra la barra de disclaimer. *(Wireframes 10; ACO-017 P4; Plan de Proyecto §1, §6)* |

## 3. Reglas de interfaz derivadas de fuentes normativas

- **Nombre del documento:** la interfaz muestra el **nombre genérico** del documento, nunca el nombre del fichero original *(Arquitectura §9; ADR-012)*. Los wireframes 2, 4 y 5 ya lo muestran así («Analítica · 12 jun 2026»).
- **Documento duplicado:** si el hash del fichero coincide con un documento del mismo paciente, se avisa y no se vuelve a procesar; el anterior sigue disponible *(Arquitectura §9; ADR-012)*. El comportamiento está en 03-REGLAS R-09 y la pantalla 3 lo recoge.
- **Etiquetas en la vista del documento anonimizado:** las de la Arquitectura §4 (`[PACIENTE]`, `[SANITARIO_n]`, `[FAMILIAR_n]`, la genérica `[PERSONA_n]`, `[HOSPITAL]`, `[FECHA_NACIMIENTO]`). El wireframe 4 usa `[SANITARIO_1]` y `[PACIENTE]`. UC-05 conserva `[MÉDICO_1]`: prevalece la Arquitectura.
- **Resultado de la validación:** en lenguaje natural, agrupado por importancia y **sin confianza, umbral, recuentos ni códigos internos** *(ACO-032 P8; Wireframes 4)*. Los valores de los umbrales se aplican en el backend y están en 03-REGLAS R-13; la interfaz no los muestra.
- **Documento retenido:** no se revisa después ni se muestra para revisión, porque no se guarda *(Arquitectura §4; ADR-013)*. La pantalla 4b solo comunica el resultado y ofrece reintentar. La revisión obligatoria llegará con el diseño del Nivel 3, que está abierto.
- **Disclaimer:** barra permanente en todas las pantallas autenticadas (2–9), con el literal de ACO-031 P2; el login no la muestra *(Arquitectura §11; Wireframes 2–9; ACO-031 P2, P5)*.
- **Origen de la respuesta:** se cita la fuente (documento, glosario o RAG) o se indica con claridad que la respuesta procede del conocimiento interno del LLM. *(Arquitectura §6; UC-09)*
- **Ocultar en el resumen** no limita la conversación. *(Arquitectura §7)*
- **Motivos del desbloqueo:** `motivo` y `motivo_resolucion` son texto libre; la interfaz no fija límite ni validación porque ninguna fuente lo hace (ver Cuestiones abiertas).

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Texto de los avisos al paciente de las pantallas 4b y 4c. Los wireframes v0.6 recogen un texto, pero ADR-013 deja fuera de su decisión el literal de los avisos. | ADR-013 (Fuera de esta decisión); Wireframes 4b, 4c |
| Diseño del Nivel 3 (pantalla 4 en S2): marcado de datos escapados y ocultación de contenido en el momento de la carga, almacenamiento temporal durante la revisión y marcado posterior. Cuando exista, el documento retenido pasará a revisión obligatoria en lugar de descartarse. | Arquitectura §16 nº 10 |
| Formatos de subida en el Sprint 1. El wireframe 3 admite «PDF, JPG, PNG · máx. 20 MB», pero el pipeline del Sprint 1 trabaja sobre texto (ACO-020) y el OCR es del Sprint 2 (ACO-051 P1; Arquitectura §4). No está definido qué acepta la interfaz mínima. | Wireframes, pantalla 3; ACO-020; ACO-051 |
| Formato exacto del nombre genérico. El wireframe muestra «Analítica · 12 jun 2026», pero ADR-012 deja abiertos el algoritmo del hash y el formato. | ADR-012 (Fuera de esta decisión); Wireframes 2, 3, 4 y 5 |
| Contenido de los campos de texto libre `motivo` y `motivo_resolucion`: pueden contener datos identificativos y ninguna fuente fija límite, validación ni anonimización. | Modelo E/R (SOLICITUD_DESBLOQUEO_CREDITO); Wireframes 8 y 9 |
| Interfaz de la solicitud de borrado (aparece en el menú del wireframe 2, sin pantalla). Su diseño está abierto. | Wireframes, pantalla 2; Arquitectura §16 nº 3 |
