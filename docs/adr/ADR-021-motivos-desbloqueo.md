# ADR-021 — Motivos de la solicitud de desbloqueo: catálogo cerrado, sin texto libre

Estado: aprobado

Sustituido por: —

Origen: Decisión conjunta #166 (abierta el 15 nov 2026; dos votos a favor y ninguna objeción registrada a 16 nov: L0C84 y mmartinez131). Recoge la ADVERTENCIA de #164 y cierra el tratamiento de los campos que abrió PD-06. Aplicación en Casos de Uso UC-23/UC-24, Arquitectura §2, §8 y §11, Modelo E/R y wireframes 8, 9 y 10; la redacción de #163 (PD-30) queda subordinada a este ADR.

Relacionados: ADR-005 (el documento original no se persiste), ADR-012 (qué se conserva del documento original), ADR-013 (política de anonimización y umbral); #163, #164, #166.

## Contexto

El Modelo E/R v0.10 incorporó a `SOLICITUD_DESBLOQUEO_CREDITO` dos campos `TEXT` libres: `motivo` (lo escribe el paciente, opcional) y `motivo_resolucion` (lo escribe el administrador, obligatorio al denegar y opcional al aprobar; el paciente lo ve en el detalle de su solicitud). Los wireframes v0.6 los muestran en las pantallas 8 y 9.

Hechos que enmarcan la decisión:

- **Ninguna fuente normativa los pide ni los regula.** UC-23 y UC-24 y la Arquitectura §8 no mencionan motivos; ningún ADR los trata; el E/R v0.10 los dejó anotados como pendiente documental. El `motivo` del paciente nació de un wireframe (PD-06) y el E/R se adaptó a él: la cadena de derivación se recorrió al revés.
- **No hay límite, validación, moderación ni anonimización fijados**, en ninguna de las dos direcciones.
- **Texto libre de cualquiera de los dos lados puede contener datos identificativos o de salud**: el paciente puede escribir su nombre, un teléfono o el motivo clínico de la consulta; el administrador puede copiar del historial el detalle de un ingreso o una analítica. Ese texto se persiste y, en el caso de la resolución, además se le muestra al paciente.
- **Las garantías de la Arquitectura están escritas para documentos clínicos.** §2 fija la privacidad por diseño y §11 protege el contenido de los documentos originales; no dicen nada de textos que escribe el paciente ni de los que se escriben sobre él. El principio no cubre el caso y hay que decidir si se extiende.
- **No hay nada implementado ni datos que migrar.** UC-23 y UC-24 no tienen sprint asignado y no existe código ni esquema desplegado: es el momento más barato para no persistir el dato.
- **Aplicar Presidio a estos textos no es «pasar por la anonimización».** Los umbrales y la fórmula de confianza están calibrados para documentos (ADR-013, R-13, R-48, ACO-023); su contrato es el de la API de anonimización de documentos. Usarlo sobre textos de 100–300 caracteres abre un uso nuevo del módulo, cambia el contrato entre áreas y destruye la legibilidad que el administrador necesita para decidir.

## Decisión

1. **Catálogo cerrado en los dos lados (A).** `motivo` es una elección de una lista cerrada y sigue siendo opcional; `motivo_resolucion` es una elección de otra lista cerrada y sigue siendo obligatoria al denegar. **No hay campo de texto libre en ninguna de las dos pantallas ni en ninguna de las dos tablas.** Desaparece el problema del límite de longitud porque deja de haber texto que limitar.

2. **Dos catálogos separados, con semilla.** `MOTIVO_SOLICITUD` y `MOTIVO_RESOLUCION` son dos entidades de clasificación distintas, no una tabla única con un campo de ámbito: no comparten valores, obligatoriedad ni redacción, y un ámbito común obligaría a una restricción cruzada en cada clave foránea. Es el precedente de `TIPO_DOCUMENTO` y `TIPO_ETIQUETA`. En `SOLICITUD_DESBLOQUEO_CREDITO` las dos columnas `TEXT` pasan a clave foránea al catálogo correspondiente; no se usan enumerados ni `CHECK` en el código, para que ampliar un catálogo no exija migración ni despliegue.

3. **Fuente y gobierno de los valores.** La lista inicial de cada catálogo se fija en la **ficha ejecutable de UC-23/UC-24**, dentro del modelo de este ADR y con tres límites: la lista es cerrada, las etiquetas se redactan para el paciente (punto 4) y ningún valor puede introducir texto libre ni campos de texto asociados. Es una delegación acotada: mientras los valores no existan, el arnés lo registra como cuestión abierta en 06-SEMILLA y **no se construye el selector**. Añadir o retirar un valor exige cambiar esa ficha y regenerar el arnés; no es decisión conjunta, porque con el modelo cerrado ya no toca privacidad, datos de pacientes ni contratos entre áreas, y lo aprueba la revisión normal de la PR. El administrador no crea ni edita valores en caliente desde la aplicación.

4. **Etiquetas redactadas para el paciente.** El motivo de la resolución se muestra en el historial del paciente (wireframe 9): un valor pensado para el operador («consumo anómalo») se lee como un juicio sobre él. Las etiquetas del catálogo de la resolución son frases neutras, en segunda persona o impersonales, comprensibles sin contexto administrativo. Es un requisito de redacción del catálogo, no una preferencia de estilo.

5. **El principio se extiende, y la protección se acota a la elección.** La Arquitectura §2 y §11 recogen la regla para estos campos, también cuando el texto lo escribe el paciente: **no se recogen ni se persisten textos libres, con independencia de cualquier tratamiento posterior. No hay nada que anonimizar porque no hay entrada.** Lo que se protege no es la etiqueta del catálogo, que es pública y aparece en la semilla, en las pruebas, en los wireframes y en la documentación, sino **la elección concreta de una persona o de una solicitud**: esa no aparece en logs, mensajes de error, fixtures, commits, documentación ni capturas, igual que el contenido de los documentos (R-04, R-56).

6. **Retención.** Al borrarse una solicitud se borra su fila y con ella su elección; el catálogo no contiene datos personales, lo comparten todas las solicitudes y **no se borra**. Un valor que ya está referenciado no se elimina: se marca inactivo, de modo que el historial del paciente siga siendo legible y el selector solo ofrezca los activos. El diseño del borrado por derecho al olvido y su verificación son del ADR pendiente del Sprint 2 (Arquitectura §16 nº 3); este ADR solo fija que ningún motivo se conserva fuera de `SOLICITUD_DESBLOQUEO_CREDITO` y que el catálogo queda fuera del borrado por no ser dato personal.

7. **No se usa el módulo de anonimización.** No se invoca Presidio para estos campos, no cambia el contrato de la API de anonimización y no se tocan ADR-013 ni sus umbrales.

8. **Orden de aplicación.** Arquitectura §2, §8 y §11 y Casos de Uso UC-23/UC-24 → Modelo E/R y wireframes 8, 9 y 10 → regeneración del arnés (02, 03, 04, 06, 07 y 08). #163 se cierra con la redacción que salga de aquí, no con la de texto libre. La regeneración del arnés va después del merge de #164, que es donde vive la cuestión abierta que este ADR cierra.

## Alternativas consideradas

- **A parcial (catálogo para el paciente y texto libre para el administrador):** descartada. Era la formulación inicial de la opción A. Deja el riesgo en el campo que además se le muestra al paciente y no es verificable: nada impide «Denegado: tras el ingreso de marzo y la analítica del 12».
- **D (quitar `motivo` y dejar solo el catálogo de la resolución):** descartada por el equipo, aunque es coherente con la minimización. Se pierde la explicación del paciente, y el administrador decide mejor con ella; con catálogo cerrado no añade riesgo.
- **B (texto libre con límite, pasado por la anonimización):** descartada. Cambia el contrato entre áreas, exige umbrales para textos cortos y una regla para el caso en que el texto no los alcance, y el resultado (`[PERSONA_1]`) deja de servir para decidir y para leer.
- **C (texto libre con límite y aviso al paciente):** descartada. Es el statu quo con una advertencia: sigue persistiendo texto libre con datos identificativos y lo sigue mostrando.
- **Texto libre del administrador con límite de longitud, sin anonimizar:** descartada por el mismo motivo que C, y con el agravante de que ese texto lo lee el paciente.
- **Un único catálogo con un campo de ámbito:** descartada. Los dos motivos no comparten valores ni obligatoriedad, y el ámbito obliga a comprobar en cada clave foránea que el valor elegido es del lado correcto.
- **Enumerado en el código o `VARCHAR` con CHECK:** descartado. Ampliar el catálogo exigiría migración y despliegue; la tabla con semilla sigue el precedente del modelo y permite crecer sin tocar el esquema.
- **Catálogo editable por el administrador:** descartado. Convierte el catálogo en texto libre con otro nombre y añade una pantalla, un permiso y un registro de cambios que nadie ha pedido.
- **Fijar aquí los valores concretos:** descartado. El ADR fija el modelo y el procedimiento; la lista de valores es contenido de la ficha, como los textos de los avisos en ADR-013.

## Consecuencias

- `SOLICITUD_DESBLOQUEO_CREDITO` cambia `TEXT` por clave foránea a dos catálogos; el Modelo E/R sube de versión.
- UC-23 y UC-24 describen qué motivo elige el paciente y cuál el administrador, y la obligatoriedad al denegar (regla de negocio que recoge #163).
- La Arquitectura gana la frase que faltaba: el principio de privacidad por diseño cubre también los textos escritos por el paciente o sobre él, y en estos campos no hay texto libre que tratar.
- Los wireframes 8 y 9 pasan de caja de texto a selector; la 9 no admite texto libre y la 10 (vista móvil) se ajusta.
- Hasta que la ficha fije los valores, 06-SEMILLA los recoge como cuestión abierta y no hay selector que construir ni prueba que verificar.
- El paciente no puede explicar un caso que no esté en la lista, y el administrador no puede justificar con sus palabras. El remedio es añadir un valor por la ficha, no un campo libre.
- Los valores se retiran, no se borran: el catálogo gana una marca de activo y el historial del paciente sigue siendo legible.
- El arnés regenera 02, 03, 04, 06, 07 y 08: desaparece la cuestión abierta y con ella la ADVERTENCIA de #164.
- No hay migración ni datos que borrar: no está implementado.

## Fuera de esta decisión

- La regla de cálculo del crédito y los topes del control de gasto (Arquitectura §16 nº 16).
- El diseño del derecho al olvido y del registro de auditoría (Arquitectura §16 nº 3; ADR pendiente del Sprint 2).
- La lista concreta de valores de los dos catálogos: contenido de la delegación del punto 3, no de este ADR.
- El texto de la pantalla y la redacción de los avisos.
- El uso del módulo de anonimización sobre textos que no son documentos, que este ADR descarta para estos campos y deja abierto en general.

## Documentos afectados

- Arquitectura del Sistema §2, §8 y §11
- Casos de Uso UC-23 y UC-24
- Wireframes, pantallas 8, 9 y 10
- Modelo E/R, `SOLICITUD_DESBLOQUEO_CREDITO` y los catálogos `MOTIVO_SOLICITUD` y `MOTIVO_RESOLUCION`
- #163 (PD-30), que se cierra con esta redacción
- Arnés: 02-DOMINIO, 03-REGLAS, 04-INTERFAZ, 06-SEMILLA, 07-INTERCAMBIO, 08-PLAN
- Plan de Trabajo §9 (registro de ADR)
