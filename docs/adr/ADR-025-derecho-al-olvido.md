# ADR-025 — Derecho al olvido: qué se borra, cómo se verifica y cómo se propaga a Keycloak

Estado: aprobado

Sustituido por: —

Origen: Issue #196 y Arquitectura del Sistema v0.10 §16 nº 3, que deja abiertos «qué se borra exactamente, cómo se verifica el borrado y cómo se propaga a Keycloak (que custodia la correspondencia email↔UUID)». Documento Operativo Sprint 2 v0.4 §6: fila del ADR, responsable Miguel, y fila de ACO-040, 12–16 h con revisión de Luis. No abre decisión conjunta aparte: el merge es la aprobación, con el plazo de 48 h del Plan de Trabajo §9.

Relacionados: ADR-001 (Keycloak custodia la correspondencia email↔UUID), ADR-005 (el original no se persiste), ADR-008 (sin datos reales hasta las salvaguardas), ADR-009 (lista blanca del piloto), ADR-011 (autenticación y roles), ADR-012 (qué se conserva del original), ADR-013 (anonimización y documento retenido), ADR-022 (texto canónico del anonimizado y su hash), ADR-024 (registro de auditoría); ACO-038, ACO-039, ACO-040, ACO-043; #138, #193, #194.

## Contexto

UC-07 promete eliminar «de forma completa y verificable» todos los datos asociados a un UUID, incluida la cuenta de Keycloak, que deja de custodiar la correspondencia email↔UUID (Casos de Uso v0.7, UC-07; ADR-001; Arquitectura §11, protección de datos). La §16 nº 3 deja abierto el procedimiento, que es lo que este ADR fija.

El Modelo E/R v0.10 §4 fija una secuencia de doce pasos y el arnés (`07-INTERCAMBIO`) la copia. Su paso 9, «borrar AUDITORIA del paciente», choca con ADR-024 §6, que prohíbe borrar esas filas: las anonimiza el rol `audit_erasure`, porque el registro tiene que poder probar que el borrado ocurrió. Aquí se ratifica ADR-024 y se corrige la secuencia; la corrección de la fuente va por el registro de seguimientos, no por este fichero.

#138 dejó fijados el límite (3 documentos por paciente) y la retención (sin caducidad mientras la cuenta esté activa), y exige un borrado mínimo por documento con confirmación y auditoría. Ninguno de los dos se reabre aquí.

El repositorio no tiene todavía capa de base de datos (`backend/pyproject.toml` no incluye SQLAlchemy ni psycopg): este ADR se escribe antes del esquema y fija lo que deben cumplir ACO-038, ACO-039 y ACO-040.

## Decisión

**1. Dos operaciones, siempre por UUID.** El borrado de la cuenta afecta a todo lo asociado a un UUID; el borrado por documento, a ese documento y a nada más. Las dos las puede pedir el paciente o el administrador (UC-07). Un paciente con dos emails son dos cuentas de Keycloak y dos UUID, y ACOMPAS no puede saberlo porque no guarda el email (ADR-001): se declara como límite, no como tarea pendiente. El borrado por documento **no arrastra la conversación que citó el documento**: los mensajes son datos de la otra operación y solo caen con la cuenta. También se declara como límite.

**2. Qué no se borra y por qué.** `EMAIL_AUTORIZADO` no se toca: la lista blanca no enlaza con el UUID y su gestión es de ACANPAN (ADR-009). `PUBLICACION` y `FRAGMENTO_RAG` son el corpus documental, no datos del paciente; la tabla de unión que los referencia cae con `MENSAJE`. `AUDITORIA` no se borra: se anonimiza (punto 7). `PACIENTE` no se borra: queda su UUID, `activo` y `creado_en` (punto 3).

**3. Secuencia del borrado de la cuenta.** La del Modelo E/R §4, corregida en el paso 9 y completada con lo que faltaba:

1. `MENSAJE`.
2. `SESION`.
3. Por cada documento: las `ETIQUETA_ANONIMIZACION`, el artefacto almacenado del anonimizado y después la fila `DOCUMENTO`, que se lleva `hash_fichero` (ADR-012) y el hash del texto canónico (ADR-022 §4).
4. `PREFERENCIA_RESUMEN`.
5. `CONSUMO_LLM`.
6. `SOLICITUD_DESBLOQUEO_CREDITO`.
7. `CREDITO_PACIENTE`.
8. `AUDITORIA`: no se borra; se anonimiza (punto 7).
9. `PACIENTE.activo = false`.
10. Cuenta de Keycloak (punto 6).
11. Evento final en `AUDITORIA` (punto 7).
12. Anonimización de las filas de `AUDITORIA` del UUID (punto 7).

El orden no es indiferente. Los hijos van antes que los padres para no dejar huérfanos si el proceso se interrumpe. El artefacto almacenado va antes que su fila porque una fila sin artefacto se puede reintentar, y un artefacto sin fila ya no se encontraría. La fila `PACIENTE` se queda con `activo = false` y sin más datos: conserva el UUID que hace falta para reintentar el borrado de Keycloak y no identifica a nadie (ADR-001).

**4. Fallo a la mitad.** Todos los pasos son idempotentes y el reintento es desde el principio, no por paso. No hay máquina de estados ni cola: el Plan de Trabajo §2 descarta las colas mientras no exista una necesidad demostrada, y el volumen del piloto no las necesita. Quien observa el estado es el administrador, con `audit_reader` y la base: la aplicación solo inserta en `auditoria` y no puede leerla (ADR-024 §4). `activo = false` significa «solicitado y pendiente» (Modelo E/R), no «hecho»: una cuenta ya borrada se reconoce porque las comprobaciones del punto 5 dan cero, ausencia y 404. Reintentar no vuelve a borrar datos del paciente, pero sí puede dejar un segundo `cuenta_borrada`: ADR-024 §5 no tiene clave de deduplicación y cada ejecución deja su evento. Se acepta así: el evento no identifica a nadie y fechar los intentos es parte de lo que hay que conservar. La operación no se da por completada —ni se responde como tal— sin evento final con resultado `exito`.

**5. Verificación del borrado.** Se comprueba antes de dar la operación por completada:

- cero filas del UUID en `MENSAJE`, `SESION`, `ETIQUETA_ANONIMIZACION`, `DOCUMENTO`, `PREFERENCIA_RESUMEN`, `CONSUMO_LLM`, `SOLICITUD_DESBLOQUEO_CREDITO` y `CREDITO_PACIENTE`;
- una sola fila en `PACIENTE`, con el UUID, `activo` y `creado_en`;
- el artefacto almacenado del anonimizado, ausente: la comprobación de existencia devuelve ausencia, sea cual sea el soporte, que sigue sin decidirse (Arquitectura §16 nº 2);
- el usuario de Keycloak, 404;
- en `AUDITORIA`, las filas del UUID con `paciente_id`, `actor_id`, `entidad_id` e `ip_origen` a nulo (punto 7).

Las cuatro primeras las comprueba la aplicación: las dos de PostgreSQL con sus propias consultas, el artefacto con la capa de almacenamiento y el usuario de Keycloak por la Admin API. La de `AUDITORIA` la comprueba el administrador con `audit_reader`, porque `acompas_app` solo puede insertar y no leer (ADR-024 §4). Como después de la anonimización ya no hay UUID por el que buscar, `audit_reader` anota el `auditoria_id` del evento final antes de ejecutar la anonimización y lo localiza por él después: es el único identificador que sobrevive. La anonimización la ejecuta el rol `audit_erasure`, no la aplicación (ADR-024 §6). La evidencia que queda es el evento final sin datos personales: dice que hubo un borrado, cuándo y con qué resultado, no de quién.

Al paciente se le responde en la propia petición, antes de que su cuenta desaparezca. **No hay confirmación por correo**: ACOMPAS no guarda su email y la cuenta se borra (ADR-001). Si el paso de Keycloak falla, la respuesta dice «incompleto, pendiente» y remite al canal de ACANPAN; no se anuncia como borrado lo que no lo está.

**6. Propagación a Keycloak.** El borrado de la cuenta va después de PostgreSQL, porque el UUID vive en la fila `PACIENTE` y es lo único que permite reintentar; y antes del evento final. Se hace con el cliente de servicio del realm `acompas` y el rol `manage-users` de `realm-management`, que es **la gestión de usuarios del realm** —crear, modificar y borrar—, más ancho que el borrado: se declara así y la credencial se gestiona como ADR-015. El borrado usa `DELETE /admin/realms/{realm}/users/{id}` (Keycloak Admin REST API, recurso Users), y el conjunto exacto de permisos efectivos de `manage-users` se confirma con la versión de Keycloak desplegada al implementar ACO-040. El `id` de usuario es el UUID; la respuesta 404 cuenta como ya borrado (idempotencia). Sin respuesta o con error no hay evento de éxito: la cuenta queda pendiente y se reintenta. La alternativa —que lo ejecute un procedimiento de operador, sin credencial privilegiada en el backend— se descarta en el S2: UC-07 y `07-INTERCAMBIO` sitúan el borrado de la cuenta en la Admin API, y un paso manual puede no darse nunca.

Además, el API rechaza cualquier petición de un UUID con `activo = false`, aunque el JWT siga vigente: sin eso, quien tuviera un token vivo podría seguir operando entre el borrado y la caducidad del token. No cambia la autenticación de ADR-011 —el token se emite y se valida igual—; añade una comprobación de estado en cada petición autenticada, y la implementa ACO-040.

**7. Qué deja en el registro de auditoría.** Por cada documento, `documento_borrado`, que ya existe en ADR-024 §1. El borrado de la cuenta añade uno con `accion = 'cuenta_borrada'`, `entidad_afectada = 'paciente'`, `actor_tipo` `paciente` o `administrador`, `resultado` `exito` o `error`, `paciente_id` con el UUID y `entidad_id` a nulo. Eso amplía ADR-024 §1 (el `CHECK` de tres eventos generales pasa a cuatro) y §2 (la enumeración de `entidad_afectada`, `documento` e `historial`, incorpora `paciente`). La lista de ADR-024 es cerrada por su propio texto, así que la ampliación entra en la PR de ADR-024 (#195), **antes de su merge**, con su revisión; este ADR la cita. Si #195 se mergea sin ella, ADR-025 no se aprueba: un ADR aprobado no se edita y haría falta uno de sustitución.

El evento final se escribe unido al UUID y, después, `audit_erasure` anula `paciente_id`, `actor_id`, `entidad_id` e `ip_origen` en todas las filas de ese UUID, incluida la del propio evento final. Quedan `accion`, `ocurrido_en`, `resultado` y `entidad_afectada`: se conserva el hecho, no el vínculo (ADR-024 §6). Es el único orden posible con una sola lectura: escrito sin `paciente_id` no podría anonimizarse después, y anonimizado antes, el evento final perdería su sujeto.

**8. Borrado por documento.** Borra las `ETIQUETA_ANONIMIZACION` del documento, su fila `DOCUMENTO` —con `hash_fichero` (ADR-012) y el hash del texto canónico (ADR-022 §4)— y el artefacto almacenado del anonimizado. Antes, el paciente confirma (#138) y después queda `documento_borrado`. No toca `PACIENTE`, `SESION`, `MENSAJE` ni Keycloak: desaparece el documento, no la conversación que lo citó (punto 1). El paciente puede volver a subir el mismo fichero, porque el hash se ha ido con la fila (ADR-012).

## Alternativas consideradas

- **Borrar las filas de `AUDITORIA` del paciente, como decía el paso 9 del Modelo E/R.** Descartada: se pierde la prueba de que el borrado se hizo y contradice ADR-024 §6, que es posterior y está propuesto en su PR (#195); este ADR lo ratifica y el plan es que #195 entre antes.
- **Borrado asíncrono con cola o con una máquina de estados.** Descartada: el Plan de Trabajo §2 descarta las colas mientras no exista una necesidad demostrada, e introducirlas exigiría un ADR propio; el reintento manual del administrador cubre el volumen del piloto.
- **Borrar primero la cuenta de Keycloak.** Descartada: se pierde el UUID antes de haber borrado PostgreSQL y no queda con qué reintentar.
- **Borrar también la fila `PACIENTE`.** Descartada: impide reintentar Keycloak si falla y no aporta privacidad, porque la fila no identifica a nadie.
- **Que el borrado de la cuenta lo ejecute un procedimiento de operador.** Queda como alternativa del punto 6; descartada en el S2 por UC-07 y por el riesgo de que no llegue a ejecutarse.
- **Anonimizar `AUDITORIA` antes del evento final.** Descartada: el evento final perdería su sujeto y no habría forma de anonimizarlo.

## Consecuencias

- **ACO-040** implementa las dos operaciones, la verificación, la respuesta al paciente y la comprobación de `activo` en cada petición.
- **ACO-038** da el modelo y las relaciones que hacen posible el orden del punto 3; **ACO-039**, el rol `audit_erasure` y la tabla donde vive el evento final.
- El registro de auditoría crece con filas sin identificadores que se conservan hasta su retención, la de ADR-024, pendiente de #194.
- **No cambian** el límite y la retención (#138, ADR-013), la autenticación (ADR-011) ni el modelo de la lista blanca (ADR-009).
- Las copias de seguridad no se tratan aquí: la Arquitectura §13 prevé backups cifrados y ninguna fuente fija qué pasa con ellos al ejercer el olvido. El borrado se verifica sobre los datos vivos y la carencia queda anotada en el registro de seguimientos.
- El paso 9 del Modelo E/R se corrige en su próxima revisión, y la secuencia del arnés (`07-INTERCAMBIO`) se regenera desde las fuentes: no se edita a mano.

## Fuera de esta decisión

- El límite de documentos y su retención: #138 y ADR-013.
- El modelo general del registro de auditoría, su retención y su purga: ADR-024, #193 y #194.
- La forma de la API y la pantalla: ACO-040.
- Dónde se guarda el anonimizado y con qué tecnología: Arquitectura §16 nº 2.
- El paciente con dos emails: límite declarado en el punto 1.
- Las copias de seguridad y su política.

## Documentos afectados

Arquitectura del Sistema §11 y §16 nº 3; Modelo E/R §4, paso 9; arnés `07-INTERCAMBIO` y `03-REGLAS`; registro de ADR del Plan de Trabajo §9. Casos de Uso UC-07 no cambia.
