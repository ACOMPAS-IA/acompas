# ADR-022 — Modelo de datos definitivo: UUID como identificador y anclaje de las etiquetas

Estado: aprobado

Sustituido por: —

Origen: Issue #189, que queda abierta tras el merge: el registro en el Plan de Trabajo §9 y la retirada de la cuestión nº 5 de la Arquitectura se hacen en `acompas-fuentes`. Cierra la cuestión nº 5 de la Arquitectura del Sistema v0.10 §16 y desbloquea ACO-038 y ACO-043 (matriz del Documento Operativo Sprint 2 v0.4 §6).

Relacionados: ADR-001 (Keycloak como custodio de la correspondencia email↔UUID), ADR-004 (OCR exclusivamente local), ADR-005 (el documento original no se persiste), ADR-012 (qué se conserva de cada documento original), ADR-013 (política de anonimización y umbral), ADR-021 (catálogos de motivos); ACO-036, ACO-038, ACO-040 y ACO-043; #138.

## Contexto

La Arquitectura §16 nº 5 deja abierto el cierre del modelo de datos: «falta cerrar el modelo de datos completo: UUID como identificador y ETIQUETA_ANONIMIZACION». El Modelo E/R v0.10 ya usa UUID en las claves primarias de sus diecisiete entidades, y `PACIENTE.paciente_id` es el UUID de Keycloak (ADR-001), así que el tipo de clave no está en discusión. Lo que falta es concretar tres cosas: la generación de los UUID que no vienen de Keycloak, la semántica de las dos columnas de posición y la declaración de que con eso el modelo queda cerrado.

Hechos que enmarcan la decisión:

- **Las posiciones llevan abiertas desde la v0.9 del E/R.** Se definían sobre el texto original; como el original no se conserva (ADR-005, ADR-012), quedaron sin sentido y sin sustitución. La nota de la entidad mantiene `posicion_fin` por compatibilidad con la salida de Presidio, mientras el control de cambios de la v0.5 todavía la llama «decisión definitiva» y el de la v0.9 la deja abierta: es la incoherencia PD-03 del arnés.
- **El Nivel 3 marca sobre el documento ya anonimizado.** Es revisión manual opcional del paciente (ADR-003): ve el documento anonimizado y señala lo que se haya escapado, seleccionando texto de esa vista. Sin un ancla en ese texto, la marca no se puede registrar en la tabla. El original no hace falta para nada de eso.
- **No hay nada implementado.** No existe esquema desplegado ni migración alguna: es el momento más barato para fijar la semántica, y cualquier decisión posterior obligaría a migrar. ACO-038 y ACO-043 están en la matriz del Sprint 2 sin ficha, esperando esta decisión.
- **La tecnología de almacenamiento no afecta al anclaje.** Que el documento anonimizado se guarde en PostgreSQL o en un volumen cifrado sigue abierto (ADR-010; §16 nº 2); lo que esta decisión exige es que su texto se conserve estable, sea cual sea el soporte.
- **Dos valores no los fija ninguna fuente**: la generación de los UUID y la unicidad de `ADMINISTRADOR.keycloak_id`. Se anotaron en #189 el 19 de noviembre de 2026 y siguen el procedimiento del Plan de Trabajo §8; entran aquí marcados como decisión nueva, con su vehículo.
- **Ya está decidido y no se reabre:** la correspondencia email↔UUID y que `paciente_id` sea el UUID de Keycloak (ADR-001); qué se conserva del documento original (ADR-012); los umbrales y el tratamiento del documento retenido (ADR-013).

## Decisión

1. **Identificador.** Todas las claves primarias del modelo son UUID. `PACIENTE.paciente_id` es el UUID de Keycloak (ADR-001) y no se duplica en otra columna. Los demás identificadores los genera la aplicación como `uuid4`, salvo los que sean clave foránea a un UUID de Keycloak. Las claves foráneas son UUID con integridad referencial, con la excepción que ya recoge el E/R: `AUDITORIA.actor_id` es una referencia polimórfica —`actor_id` con `actor_tipo`—, no una FK estricta. Con esto el modelo queda cerrado en su tipo de clave.

2. **A qué texto se anclan las etiquetas.** `posicion_inicio` y `posicion_fin` se refieren al **texto canónico del documento anonimizado**, que es el que guarda `DOCUMENTO.ruta_almacen`. El intervalo es semiabierto `[inicio, fin)`, con base 0, y se cuenta **en puntos de código** sobre el mismo texto que se almacena, sin normalización Unicode posterior. El anclaje al texto anonimizado lo decidió #189 el 19 de noviembre de 2026; la unidad, el intervalo y la base los fija este ADR para que la decisión sea ejecutable. Nunca al documento original.

3. **Cuándo se calculan y qué filas lo llevan.** La detección y la marca ocurren siempre sobre un texto existente; como la sustitución por `[SANITARIO_1]` desplaza los desplazamientos siguientes (`replacement.py:131-132`), estos se **trasladan** a las coordenadas del texto canónico una vez aplicadas todas las sustituciones. Se escriben al crear la fila, tanto para `fuente='presidio'` como para `fuente='paciente'`, y no se recalculan después; `numero` sigue localizando la etiqueta con independencia de la posición. Las columnas son **`NOT NULL`** por construcción: la fila existe solo si hubo detección o marca, y el documento cuyo texto extraído está vacío es ilegible —no se procesa y se avisa (ADR-013; R-50)—, así que nunca llega a tener etiquetas.

4. **El texto canónico no es un dato aparte.** Es la representación textual del documento anonimizado, y debe ser la misma sobre la que el paciente marca en el Nivel 3: si la vista aplica formato o paginación, la conversión entre ambas la resuelve ACO-036. Debe almacenarse de forma que no haya que regenerarla, porque una segunda extracción puede dar otro texto e invalidar todas las posiciones, y **el documento guarda el hash de ese texto**: si el texto no coincide con su hash, las posiciones se consideran inválidas y el documento se procesa de nuevo. Es parte del documento anonimizado, no una copia nueva, y **se borra con él** en el derecho al olvido (§16 nº 3, ACO-040); sin él las posiciones no son verificables.

5. **Decisiones nuevas, registradas.** `uuid4` para los identificadores generados por la aplicación y `ADMINISTRADOR.keycloak_id` como `UNIQUE NOT NULL` (hoy solo `NOT NULL`) no los fija ninguna fuente. Se registraron en #189 el 19 de noviembre de 2026 y siguen el Plan de Trabajo §8: entran en este ADR y se aprueban con él, con la revisión de la PR como objeción y su plazo de 48 h; si la revisión considera que alguna es una cuestión de arquitectura abierta, no se aprueba dentro del ADR y pasa a decisión conjunta. Si el §8 no resuelve la unicidad de `ADMINISTRADOR.keycloak_id`, se retira de este ADR y queda en el registro de seguimientos: no condiciona el cierre del modelo.

6. **Paciente y Keycloak.** No hay decisión nueva: se deja escrito que `paciente_id` es el UUID de Keycloak (ADR-001) y que no se guarda una segunda correspondencia, para que no se reabra al implementar.

## Alternativas consideradas

- **Anclar al texto original:** descartada. El original no se conserva (ADR-005, ADR-012), y con los valores y sus posiciones se podría reconstruir.
- **Eliminar `posicion_inicio` y `posicion_fin`:** descartada. El Nivel 3 necesita registrar sobre qué tramo del documento anonimizado está la marca, y `numero` identifica la etiqueta, no el tramo.
- **Rellenar solo las etiquetas de `fuente='paciente'`:** descartada. Dejaría la misma columna con dos reglas de lectura según la fuente, y las detecciones automáticas también necesitan su ancla para pintarse y verificarse.
- **Medir en bytes o en unidades UTF-16:** descartada. La unidad depende de la codificación y del lenguaje; el punto de código es estable sobre el texto almacenado.
- **Generar los UUID en la base de datos:** descartada. Hacen falta antes de escribir la fila, para componer la respuesta y para encadenar la anonimización, y generarlos en dos sitios complica la idempotencia.
- **UUIDv7 o ULID, que ordenan por tiempo:** descartada. El orden de creación ya lo da `creado_en` en cada entidad, y no se justifica una dependencia por una ventaja que no se usa.
- **Guardar el texto canónico como un artefacto derivado que se regenera al leer:** descartada. Una segunda extracción puede producir otro texto y mover todos los desplazamientos.

## Consecuencias

- **ACO-038** implementa el modelo tal como queda: UUID, columnas de posición `NOT NULL` y el campo de hash del texto anonimizado.
- **ACO-043** almacena el texto canónico de forma estable y su hash, sin regenerarlo al leer; su ciclo de vida y el límite de documentos siguen siendo suyos (#138).
- **ACO-040** borra el documento anonimizado, su texto canónico y su hash en el borrado por documento.
- **ACO-036** convierte los desplazamientos entre lo que el paciente marca en pantalla y el texto canónico, y decide qué ocurre con las marcas del paciente si el documento se reprocesa.
- **El hash del texto anonimizado no sustituye a `hash_fichero`** (ADR-012): el primero invalida posiciones cuando el texto cambia, el segundo detecta subidas repetidas del mismo fichero original.
- **No hay migración**: no existe esquema desplegado. El modelo nace ya con esta forma.
- **El modelo queda cerrado** con diecisiete entidades y UUID, y la cuestión nº 5 de la Arquitectura puede retirarse.

## Fuera de esta decisión

- El comportamiento del Nivel 3 y el tratamiento del documento retenido (ACO-036; Arquitectura §16 nº 10; ADR-013).
- El ciclo de vida, el límite y la retención de documentos (#138; ACO-043).
- El diseño y la verificación del borrado (§16 nº 3; ACO-040): aquí solo se fija que el texto canónico se borra con el documento.
- El modelo del registro de auditoría (§16 nº 4).
- El almacenamiento de objetos (§16 nº 2; ADR-010).
- El formato de entrada del Sprint 1 (PD-07).
- Tablas, índices y migraciones concretas: son de ACO-038.
- Los catálogos y los motivos de ADR-021, que no se tocan.

## Documentos afectados

Por este orden, en `acompas-fuentes` y por encargo:

1. **Modelo E/R v0.11:** retirar la cuestión abierta de `posicion_inicio` y `posicion_fin`, alinear la nota de la entidad y el control de cambios, añadir el campo de hash del texto anonimizado en `DOCUMENTO` y el `UNIQUE` de `ADMINISTRADOR.keycloak_id`, si el Plan de Trabajo §8 lo mantiene. Cierra PD-03 del arnés.
2. **Arquitectura del Sistema, §16 nº 5:** retirar la cuestión.
3. **Arnés 02 y 07:** regenerar, una vez actualizadas las dos fuentes anteriores.
4. **Plan de Trabajo, §9:** incorporar ADR-022 al registro de ADR, junto con ADR-019, ADR-020 y ADR-021, que hoy faltan.
