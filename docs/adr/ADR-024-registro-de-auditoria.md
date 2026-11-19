# ADR-024 — Registro de auditoría: eventos, identificadores y detalle físico

Estado: propuesto

Sustituido por: —

Pendiente: la decisión conjunta #194 sobre la retención de la tabla general y su purga. Pasa a `aprobado` al cerrar esa ventana sin objeción, antes del merge.

Origen: Issue #193 y Arquitectura del Sistema v0.10 §16 nº 4; cierra el modelo que #81 dejó fijado para el documento retenido (A1 + B1-S2, 29 oct 2026) y la lista de eventos de §11. Documento Operativo Sprint 2 v0.4 §6, fila de ACO-039 (Miguel).

Relacionados: ADR-007 (PostgreSQL única base de datos), ADR-008 (sin datos reales hasta las salvaguardas), ADR-011 (autenticación y roles), ADR-013 (política de anonimización y documento retenido), ADR-015 (secretos); ACO-025, ACO-038, ACO-039, ACO-040; #138, #194.

## Contexto

La Arquitectura §11 exige un registro de auditoría de accesos y operaciones sensibles y nombra tres: carga de documentos, borrados y accesos al historial. La §16 nº 4 deja abiertos «qué eventos quedan registrados y qué identificador se usa para cada entrada». El Modelo E/R v0.10 describe una entidad `AUDITORIA` general, con actor polimórfico, `paciente_id`, `entidad_afectada`, `entidad_id`, `ip_origen`, `resultado`, un `detalle` de texto libre y `creado_en`; el índice previsto es `paciente_id` + `creado_en`.

#81 cerró el mínimo del documento retenido: un evento por retención con fecha UTC sin hora, tipo de documento y motivo de enumeración cerrada; sin texto, contenido, nombre de fichero, `paciente_id`, id de petición, usuario, IP ni texto libre; tabla dedicada, la aplicación solo inserta, retención de seis meses y lectura por `audit_reader`. No decidió los eventos generales ni el detalle físico.

ADR-008 hace de la auditoría una condición para usar documentos reales: la demo interna con documentos reales depende de que ACO-039 esté operativo.

Hoy no hay capa de base de datos en el repositorio: `backend/pyproject.toml` no incluye SQLAlchemy, Alembic ni psycopg. El ADR se escribe antes de que exista el esquema.

#81 asignó la implementación a ACO-025, «ampliando su alcance»; el Documento Operativo Sprint 2 v0.4, posterior, la asigna a ACO-039 y no incluye ACO-025. Prevalece el acto posterior.

## Decisión

**1. Lista cerrada de eventos.** Se registran cuatro:

| `accion` | Cuándo |
|---|---|
| `documento_cargado` | El paciente carga un documento que se procesa |
| `documento_borrado` | Se borra un documento, por derecho al olvido o por el administrador |
| `historial_consultado` | Se abre el historial del paciente |
| `documento_retenido` | El documento se retiene por baja confianza (#81) |

No se registran, y el ADR lo dice para que no entren por la vía de los hechos: `inicio_sesion` (lo cubre Keycloak, ADR-011), `confirmacion_anon` (no es acceso, carga ni borrado; su rastro está en `DOCUMENTO.validado_en`), la consulta o edición del documento anonimizado, los desbloqueos de crédito y los accesos directos del administrador a `psql`, que no pasan por la aplicación. Añadir un evento exige modificar este ADR.

**2. Identificador y relación con la entidad.** Cada fila lleva `auditoria_id` UUIDv4 interno, generado por el servidor, nunca expuesto ni reutilizado en otro sistema. El actor se identifica con `actor_id` y `actor_tipo` (`paciente`, `administrador` o `sistema`). El sujeto afectado es `paciente_id`, el UUID que el sistema usa como seudónimo: ninguna entidad guarda la identidad real (ADR-001). La entidad concreta se identifica con `entidad_afectada`, de enumeración cerrada (`documento`, `historial`), y `entidad_id`, el UUID del registro afectado; no se copia contenido, nombre de fichero, identificador de petición ni texto libre. `documento_retenido` no lleva paciente, actor ni entidad, porque no hay entidad persistida a la que apuntar (#81).

**3. Dos tablas.** `auditoria` guarda los tres eventos generales, con las columnas del Modelo E/R **sin `detalle`** (precedente de ADR-021: no hay campos de texto libre, porque admiten contenido clínico) y con `ip_origen`; `creado_en` pasa a `ocurrido_en`, TIMESTAMPTZ en UTC. `ip_origen` es dato personal: se conserva solo aquí —#81 lo excluye del retenido— porque saber desde dónde se accede es el objeto de la auditoría de accesos, y cae con la retención de la fila. `auditoria_retencion` guarda `documento_retenido` con la forma de #81: `id` UUIDv4, `ocurrido_en` DATE en UTC sin hora, `tipo_documento` (con `desconocido` mientras no se pida) y `motivo`, que solo admite `baja_confianza`. El `id` se conserva aunque #81 permita omitirlo: fecha, tipo y motivo admiten duplicados y la tabla necesita clave primaria; es interno y no se expone.

Son dos tablas y no una con columnas nulas porque #81 prohíbe identificadores en el retenido y los privilegios tienen que poder diferir por tabla; una tabla común dejaría escribir un `paciente_id` junto a un evento de retención y no habría forma de impedirlo por permiso.

Retención: seis meses naturales en ambas, contados desde `ocurrido_en`. Índices: `auditoria(paciente_id, ocurrido_en)`, `auditoria(ocurrido_en)` y `auditoria_retencion(ocurrido_en)` para la purga; ninguno que facilite cruces por tipo o motivo.

**4. Privilegios.** La aplicación solo puede `INSERT` en las dos tablas: no lee, no modifica y no borra. `audit_reader` solo puede `SELECT`, y es el canal del administrador en S2, por `psql`. `audit_retention` solo puede `EXECUTE` una función `SECURITY DEFINER` que borra los registros vencidos y calcula el corte internamente, sin parámetros de fecha; su propietario es un rol dedicado no superusuario, con `search_path` fijado, nombres cualificados y `EXECUTE` revocado de `PUBLIC` (condiciones de #81). La supresión del derecho al olvido usa el mismo patrón con el rol `audit_erasure` (punto 6). Ningún rol de aplicación tiene `UPDATE` ni `DELETE` directos. Los roles los crea el despliegue, no la migración, y su contraseña va por el mecanismo de ADR-015. Una migración Alembic crea las dos tablas, los índices y los `GRANT`/`REVOKE`.

**5. Fallo del `INSERT` e idempotencia.** Sin evento no hay operación. Si la operación y el evento comparten transacción, se confirman juntos: si el evento falla, la operación no se completa y se devuelve error sin persistir nada. Cuando no la comparten —el borrado del documento anonimizado, cuya tecnología de almacenamiento sigue abierta (Modelo E/R `ruta_almacen`; Arquitectura §16 nº 2)—, el evento lleva el resultado real: `exito` solo después de que el almacén confirme, `error` si falla, y la operación no se da por completada sin su evento. Es coherente con ADR-008, que exige el registro operativo antes de usar datos reales. No hay clave de deduplicación, porque #81 prohíbe identificadores de correlación: dos peticiones que acaban en retención dejan dos eventos.

**6. Supresión.** Qué se borra y cuándo es de ACO-040; aquí se fija el resultado y quién puede tocarlo. Del paciente borrado quedan `accion`, `ocurrido_en`, `resultado` y `entidad_afectada`, que no identifican a nadie; pasan a `NULL` `paciente_id`, `actor_id`, `entidad_id` e `ip_origen`. El `UPDATE` solo lo hace el rol `audit_erasure` mediante función `SECURITY DEFINER`; ni la aplicación, ni `audit_reader`, ni `audit_retention` pueden modificar filas. Se conserva el hecho, no el vínculo. `auditoria_retencion` no se toca: no contiene datos personales y cae por retención.

**7. Conciliación con #81 y encaje.** ACO-039 implementa las dos tablas, los roles y la purga; ACO-025 conserva su alcance y su P5 —en S1 no persiste nada— y no cambia. El registro de auditoría de ADR-013 se aplica desde el Sprint 2, porque en S1 solo hay documentos sintéticos (ADR-008); ADR-013 no se edita. T-10 sigue abierto y se cierra con ACO-039.

**8. Pendientes de aprobación explícita.** Dos, por tocar privacidad y no estar en ninguna fuente: la **retención de `auditoria`** y la **purga de esa tabla**. Se votan en #194 con la ventana de 48 h del Plan de Trabajo §8; hasta que cierre, este ADR queda `propuesto`. La retención y la purga de `auditoria_retencion` no están aquí: las fijó #81 y se ratifican.

## Alternativas consideradas

- **Una sola tabla con columnas nulas.** Descartada: los privilegios no pueden impedir por fila que se escriba un `paciente_id` junto a un evento de retención, que es justo lo que #81 prohíbe.
- **`motivo`, `accion` o `detalle` como texto libre.** Descartada: ADR-021 ya retiró el texto libre de los campos que escribe una persona, y aquí podría contener contenido clínico.
- **Conservar `detalle` con un límite de longitud.** Descartada: el límite no impide que el texto identifique al paciente.
- **Purga ejecutada por la aplicación.** Descartada por #81 y ADR-007: la aplicación solo inserta; el borrado por antigüedad es de un job independiente.
- **`ip_origen` también en `auditoria_retencion`.** Descartada por #81.

## Consecuencias

- ACO-039 tiene ya el modelo que necesitaba: dos tablas, cuatro roles y una migración. Su ficha ejecutable los concreta al empezar, como primer commit de su PR.
- El Modelo E/R cambia: `AUDITORIA` pierde `detalle`, `creado_en` pasa a `ocurrido_en`, la enumeración de `accion` se cierra en cuatro valores y el índice de `paciente_id` + `ocurrido_en` se mantiene. Se añade `AUDITORIA_RETENCION`.
- La Arquitectura §16 nº 4 puede retirarse una vez actualizada, y la §11 puede referir este modelo.
- #81 exigía la Arquitectura §16.4 en la misma actuación que el ADR. Este repositorio no edita fuentes oficiales: el encargo sale con esta PR, §16.4 se actualiza después y la desviación queda escrita en la PR y en `docs/seguimientos.md`.
- La aplicación gana una dependencia real de base de datos y de roles que hoy no tiene; entra con ACO-039, no con este ADR.
- ACO-039 asume lo que #81 dejó encargado: PostgreSQL y los roles en la CI para probar persistencia y privilegios, y la dependencia de ACO-038 para el modelo UUID.

## Fuera de esta decisión

- La implementación: ACO-039, con ACO-038 para el modelo UUID.
- La política de retención de documentos y el documento retenido: ADR-013 y #138.
- El derecho al olvido: Arquitectura §16 nº 3 y ACO-040; aquí solo se fija qué deja el borrado en el registro.
- Autenticación, roles de usuario y sesión: ADR-011.
- Endpoint o pantalla de consulta: en S2 no hay, y el canal es `psql` con `audit_reader`.
- El `resultado` y el `detalle` de los errores de la aplicación: son logs, no auditoría.

## Documentos afectados

Por orden: Arquitectura §16 nº 4 (retirar) y §11 (referir el modelo) → Modelo E/R (`AUDITORIA` sin `detalle`, enumeración de `accion`, `creado_en`→`ocurrido_en`, índice, nueva `AUDITORIA_RETENCION` y reparto de privilegios) → arnés 02, 03, 05 y 09, con `MANIFIESTO.md` → Plan de Trabajo §9, fila de ADR-024, con las que falten. Las fuentes se actualizan por encargo en `acompas-fuentes` y el arnés se regenera después; no se editan a mano.
