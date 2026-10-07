# 04 — INTERFAZ

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Pantallas, flujos y comportamientos de interfaz que se pueden implementar, con indicación de lo que corresponde al Sprint 1.

## Qué no contiene

- Diseño visual definitivo (colores, tipografía): los wireframes son esquemáticos.
- Textos definitivos de la interfaz, salvo los que fija una fuente.
- Contratos de API: están en 07-INTERCAMBIO.

## Fuentes

- **Normativas:** Plan de Proyecto (§4); Arquitectura del Sistema (§3 Recorrido de una consulta, §4, §6, §7, §8, §9, §11, §14).
- **Derivadas:** Casos de Uso (§2, §3); Wireframes MVP (pantallas 1 a 9). Wireframes y Casos de Uso definen la interacción; ninguno puede contradecir a una fuente normativa *(Estrategia §4.6)*.

## 1. Flujo del Sprint 1 (interfaz mínima de la demo)

*(Plan de Proyecto §4, S1; Arquitectura §3, §14 fila S1; UC-01, UC-03, UC-04, UC-05, UC-06, UC-08)*

Login con 2FA (Keycloak) → acceso solo si el email está en la lista blanca → subida de un documento oncológico **sintético** → anonimización de Nivel 1 con validación por umbral → pregunta sobre el documento → respuesta de Claude con el disclaimer visible.

- Si la confianza es baja, el documento se retiene y no se completa la carga *(UC-06; Wireframes, pantalla 4)*. Lo que ve el paciente en ese caso está abierto.
- Según la Arquitectura §14, en el Sprint 1 no hay historial persistente (S3), Niveles 2 y 3 (S2), RAG (S3+), resumen ni preferencias (S5). Los ACO concretos de la interfaz del Sprint 1, sus exclusiones y los criterios de la demo están en 08-PLAN, y su verificación, en 09-TESTS.

## 2. Pantallas

La columna «Sprint» sale del Plan de Proyecto §4 y de la Arquitectura §14. Cuando una pantalla se reparte entre sprints (3, 4 y 5), qué parte toca al Sprint 1 es una **inferencia** de esas fuentes, no una decisión; el alcance exacto lo fija la ficha del ACO (08-PLAN).

| Nº | Pantalla | Casos de uso | Sprint según la planificación | Comportamiento con fuente |
|---|---|---|---|---|
| 1 | Login | UC-01 | S1 | Usuario o email, contraseña y segundo factor (código de app autenticadora). Autenticación vía Keycloak OIDC; se emite un JWT con expiración; 2FA obligatorio. *(Wireframes 1; UC-01; Arquitectura §3, §11)* |
| 2 | Mi panel | UC-17, UC-18, UC-10 | S3 (panel básico) | Lista de conversaciones (título, tema, documentos, última actividad); documentos cargados; acceso a subir, conversar, resumen, preferencias, solicitar borrado y cerrar sesión. Los documentos se comparten entre todas las sesiones. *(Wireframes 2; Plan de Proyecto §4)* |
| 3 | Subir documento | UC-04 | S1 (versión mínima) | Selección del fichero, tipo de documento (Informe de patología, Analítica, Carta de oncología, Otro) y aviso de que el documento pasará por anonimización automática. «Subir y anonimizar» dispara UC-05. *(Wireframes 3; UC-04)* |
| 4 | Validación automática + revisión manual | UC-05, UC-06, UC-20 | S1: resultado de la validación · S2: revisión manual (Nivel 3) | Muestra el resultado validado (entidades detectadas, confianza y umbral) y la vista del texto anonimizado con etiquetas. En el Nivel 3, el paciente puede seleccionar texto y marcarlo como dato identificativo escapado; es opcional («No he encontrado nada más»). Cada marca se registra en ETIQUETA_ANONIMIZACION. *(Wireframes 4; UC-20; Arquitectura §4, §9)* |
| 5 | Conversación | UC-08, UC-09, UC-11 | S1: pregunta y respuesta con disclaimer · S3+: historial, preguntas sugeridas y fuentes RAG | Burbujas de usuario y asistente; cita de la fuente de la respuesta; barra de disclaimer permanente: «ACOMPAS no diagnostica ni sustituye al médico. Ante cualquier duda, consulta siempre con tu equipo oncológico.» Aviso de sistema al empezar a consumir el crédito acumulado. *(Wireframes 5; Arquitectura §8, §11)* |
| 6 | Mi resumen | UC-12, UC-13 | S5 | Resumen generado aplicando las preferencias activas, guía de primeros pasos, preguntas sugeridas y exportación a PDF. *(Wireframes 6; Arquitectura §7)* |
| 7 | Mis preferencias del resumen | UC-21, UC-22 | S5 | Tabla Tipo (Ocultar/Anotar), Campo o sección, Texto, Alcance («Siempre»); editar y eliminar. Las preferencias **no** se crean aquí: se piden en la conversación y la app pide confirmación. Ocultar no afecta al chat. *(Wireframes 7; Arquitectura §7)* |
| 8 | Solicitar desbloqueo | UC-23 | No fijado | Se ofrece al agotar el tope diario y el crédito acumulado; muestra el estado «Pendiente de aprobación del administrador». *(Wireframes 8; Arquitectura §8)* |
| 9 | Admin · Desbloqueos | UC-24 | No fijado | Lista de solicitudes (UUID del paciente, fecha, estado) con Aprobar o Denegar. El desbloqueo es siempre manual. *(Wireframes 9; Arquitectura §8)* |

## 3. Reglas de interfaz derivadas de fuentes normativas

- **Nombre del documento:** la interfaz muestra el **nombre genérico** del documento, nunca el nombre del fichero original *(Arquitectura §9)*. Los wireframes 2, 4 y 5 muestran nombres como «analitica_junio.pdf»: una fuente derivada no puede contradecir a una normativa, así que prevalece la Arquitectura. La discrepancia está registrada como pendiente en INFORME-GENERACION.
- **Documento duplicado:** el sistema detecta subidas repetidas del mismo fichero *(Arquitectura §9)*. El comportamiento ante un duplicado está en 03-REGLAS R-09. Ni los Casos de Uso ni los Wireframes tienen todavía ese aviso, que es posterior al Sprint 1.
- **Disclaimer** permanente en la interfaz y en las respuestas. *(Arquitectura §11; Wireframes 5)*
- **Origen de la respuesta:** se cita la fuente (documento, glosario o RAG) o se indica con claridad que la respuesta procede del conocimiento interno del LLM. *(Arquitectura §6; UC-09)*
- **Ocultar en el resumen** no limita la conversación. *(Arquitectura §7)*

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Qué ve o hace el paciente con un documento retenido por baja confianza. UC-06: «se retiene para que lo revise el paciente». Wireframe 4: «se habría retenido… en vez de mostrarse aquí». Pendiente de ADR. | Plan de Trabajo §9; UC-06; Wireframes, pantalla 4 |
| Valor del umbral: el wireframe 4 muestra «umbral mínimo: 0.85» solo como ejemplo. | Plan de Trabajo §9 |
| Formatos de subida en el Sprint 1. El wireframe 3 admite «PDF, JPG, PNG · máx. 20 MB», pero el pipeline del Sprint 1 trabaja sobre texto (ACO-020) y el OCR es del Sprint 2 (ACO-051 P1; Arquitectura §4). No está definido qué acepta la interfaz mínima. | Wireframes, pantalla 3; ACO-020; ACO-051 |
| Campo «Motivo (opcional)» de la solicitud de desbloqueo: no existe en el Modelo E/R. | Wireframes, pantalla 8; Modelo E/R |
| Texto del aviso de documento duplicado y formato exacto del nombre genérico. | ADR-012 (Fuera de esta decisión); pasada B de la Estrategia (Casos de Uso y Wireframes) |
| Punto exacto de la interfaz donde va el disclaimer del Sprint 1: «el punto definido por UX». Los Wireframes lo sitúan en una barra fija de la conversación. | ACO-031; Wireframes, pantalla 5 |
| Interfaz de la solicitud de borrado (aparece en el menú del wireframe 2, sin pantalla). Su diseño está abierto. | Wireframes, pantalla 2; Arquitectura §16 nº 3 |
