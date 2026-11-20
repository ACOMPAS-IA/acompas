# ADR-027 — Diseño del Nivel 3: marcado de datos escapados por el paciente

Estado: aprobado

Sustituido por: —

Origen: Issue #200, que recoge las decisiones del responsable del 20 de noviembre de 2026, y Arquitectura del Sistema v0.10 §16 nº 10, que deja abierto el diseño del Nivel 3. Documento Operativo Sprint 2 v0.4 §6: fila «Nivel 3», que escribe Miguel con Luis en el criterio clínico, y fila ACO-036 (10–14 h), que este ADR desbloquea. D2 y D2 bis se registran en #200 con su línea de veredicto y 48 h, porque afectan a datos reales y a privacidad (Plan de Trabajo §8); el resto de la Issue es la redacción de lo ya decidido.

Relacionados: ADR-003 (anonimización en tres niveles), ADR-005 y ADR-012 (el original no se persiste), ADR-008 (sin datos reales hasta las salvaguardas), ADR-013 (política de anonimización y umbrales), ADR-022 (modelo de datos y anclaje de posiciones; PR #190, en revisión), ADR-023 (OCR y confianza del documento; PR #192, en revisión), ADR-024 (registro de auditoría; PR #195, en revisión); ACO-035, ACO-036, ACO-037, ACO-046; #53 y #161.

## Contexto

La Arquitectura define la anonimización en tres niveles. El Nivel 3 es la revisión manual del propio paciente sobre el documento ya anonimizado por los Niveles 1 y 2: si detecta un dato que se ha escapado, lo marca él mismo. No es una segunda pasada del modelo (R-14). La Arquitectura §16 nº 10 deja abierto su diseño: «marcado de datos escapados y ocultación de contenido en el momento de la carga, almacenamiento temporal durante la revisión y marcado posterior».

La misma sección se contradice en el cuándo. La etapa 2 del §4 dice que los documentos pasan por los Niveles 1–3 «antes de entrar en el sistema»; la definición del Nivel 3 lo llama «un paso posterior y opcional». La diferencia no es de redacción: si la marca se hace después de que el documento se haya usado, la copia guardada queda corregida pero el dato escapado ya viajó a la API, y la sustitución sería cosmética.

El Modelo E/R ya admite la marca: `ETIQUETA_ANONIMIZACION.fuente` vale `'presidio'` o `'paciente'`, y sus posiciones quedan como cuestión abierta que ADR-022 cierra anclándolas al texto canónico del documento anonimizado (PR #190, en revisión). ADR-013 fija los umbrales y el tratamiento del documento retenido y no entra aquí; ADR-023 deja también fuera el Nivel 3 (PR #192, en revisión). ADR-008 exige que la anonimización esté resuelta antes de usar datos reales.

## Decisión

**1. Qué hace una marca: sustituye (D1).** El paciente selecciona un tramo del documento ya anonimizado y pulsa un botón; el tramo queda tapado por la etiqueta `[MARCA_USUARIO]`. No es solo un registro: el dato desaparece de lo que se guarda y de lo que se usa. Lo que se persiste es el tramo y su etiqueta, nunca el texto marcado: guardar el contenido sería persistir justo el dato que se ha escapado.

**2. Cuándo: antes del primer uso, y con qué puerta (D1 bis).** La revisión precede a que el documento participe en la conversación. Así se resuelve la contradicción del Contexto en el sentido del §4. La condición de uso se expresa con los valores que ya tiene `estado_anon`: `pendiente` mientras falta la revisión y `validado` cuando el documento ha pasado los Niveles 1–3. No se añade ningún valor nuevo; si ACO-036 necesitara un tercero, exigiría su propio ADR.

**3. El Nivel 3 forma parte de la anonimización (D2).** «La anonimización» que ADR-008 exige antes de usar datos reales comprende los Niveles 1, 2 y 3. No se edita ADR-008: se declara aquí. Consecuencias: ACO-036 pasa a ser puerta de los documentos reales —sin él no entra ninguno, tampoco el del responsable—; la demo depende de que cierre antes de la demo, cuya fecha sigue pendiente de #161; y la cadena arranca en ADR-023 (PR #192, en revisión) y sigue en ACO-035. Si 036 se retrasa, se aplica el plan B ya escrito en la Arquitectura: documentos anonimizados fuera de la aplicación.

**4. Lo que no incluye: el documento retenido (D2 bis).** No se revisa el documento que no superó el umbral de documento: sigue descartándose como hoy. Llevarlo a revisión obligatoria exige guardar temporalmente un documento que puede contener datos identificativos, y eso es una decisión de privacidad con su propio procedimiento, no un añadido de este ADR. Queda fuera y se declara fuera.

**5. Las posiciones se trasladan; no se recalculan.** El tramo se ancla al texto canónico del documento anonimizado, en el intervalo `[inicio, fin)` con base 0 (ADR-022, punto 2, en revisión). Sustituir un tramo cambia el texto, así que el traslado de las etiquetas posteriores es una traducción de coordenadas al texto nuevo, no un recálculo de filas existentes: las posiciones se escriben una vez y no se recalculan (ADR-022, punto 3, en revisión), y las nuevas se calculan sobre el texto resultante. El hash del texto se recalcula en el mismo acto; si no coincide, las posiciones son inválidas y el documento se procesa de nuevo (ADR-022, punto 4, en revisión).

**6. `[MARCA_USUARIO]` es un tipo nuevo del catálogo.** Su etiqueta es `[MARCA_USUARIO]` y su `tipo_entidad` es `'MARCA_USUARIO'`, con `fuente='paciente'`. `numero` toma el siguiente del documento y la etiqueta visible no lleva numeral, para no renumerar `[SANITARIO_n]`. El catálogo exacto sigue abierto en el Modelo E/R y este ADR no lo cierra más allá de esta fila.

**7. `confirmada` no significa lo mismo en una marca manual.** En las marcas manuales vale `false`: la columna dice si la detección superó el umbral automático y una marca no supera nada. Se alinea la nota del campo, y la cobertura y la auditoría deberán filtrar por `fuente` antes de leerlo cuando existan; hoy no hay ningún consumidor.

**8. La métrica publica dos cifras.** Cada marca se registra, y la métrica publica marcas totales y marcas sobre términos de la lista de ADR-013. Así no se elige la lectura que embellece el número ni la que lo hunde. La publicación corresponde a las métricas de cobertura (ACO-037).

**9. El límite, declarado.** Hay datos que identifican sin estar en ningún campo, por combinación —una enfermedad poco frecuente con una fecha y un centro—; ADR-013 decidió no anonimizar las fechas que no sean la de nacimiento, la edad, el sexo, la profesión ni el país. Eso no se puede medir y se declara por escrito que no se mide. Es un límite de medición, no una pregunta clínica.

**10. El texto seleccionado no se registra.** No va a auditoría, ni a logs, ni a telemetría: solo el hecho de la marca, su tramo y su etiqueta.

## Lo que este ADR propone y no decide por sí solo

- **Las 48 h de D2 y D2 bis.** Se registran en #200; si alguna se objeta, el ADR se corrige antes del merge.
- **La publicación de las dos cifras.** Corresponde a las métricas de cobertura (ACO-037).

## Alternativas consideradas

- **Registrar la marca sin sustituir.** Descartada: el dato escapado seguiría en lo guardado y en lo que se usa; la marca sería un aviso, no una corrección.
- **Marcar después del primer uso.** Descartada: la copia quedaría corregida, pero el dato ya habría viajado a la API.
- **Redacción libre por el paciente.** Descartada: introduce contenido nuevo sin límite ni validación y complica la trazabilidad.
- **Guardar el texto marcado para auditar.** Descartada: persiste justo el dato que se ha escapado.
- **Reutilizar un tipo existente del catálogo.** Descartada: falsea la procedencia de la marca y la métrica de las dos cifras.

## Consecuencias

- **La Arquitectura cambia de frase, no la interfaz.** §16 nº 10 anuncia que el documento retenido pasará a revisión obligatoria; D2 bis lo descarta, así que esa frase se corrige en la próxima revisión. UC-20 y el wireframe 4b ya lo descartan y no cambian por este ADR.
- **Las filas de marca llevan posiciones.** Se escriben al crear la fila, como las de Presidio, y con `confirmada=false`; el alta de ACO-036 no puede omitirlas.
- **El documento no se usa hasta estar `validado`.** ACO-036 lo implementa con el modelo actual y no puede introducir estados nuevos sin ADR.
- **Las dos cifras de la métrica** se publican con las métricas de cobertura (ACO-037); el límite del punto 9 se escribe junto a ellas.
- **036 es condición necesaria, no suficiente.** ADR-008 y la regla R-01 siguen vigentes y exigen también el derecho al olvido y la auditoría operativos; la demo con documentos reales espera a la puerta y a la fecha de #161.

## Fuera de esta decisión

- **El documento retenido por baja confianza** y su revisión obligatoria (punto 4): decisión de privacidad con su propio procedimiento.
- **Los umbrales de anonimización** y el tratamiento del documento retenido: ADR-013.
- **A qué texto se anclan las posiciones:** ADR-022.
- **La validación reforzada de entidades y el OCR:** ADR-023 y ACO-035.
- **El catálogo completo de tipos de entidad** y el nombre de las etiquetas automáticas: ADR-012, ADR-013 y el Modelo E/R.
- **La pantalla del paciente más allá de lo que el Nivel 3 necesita:** ACO-046.

## Documentos afectados

1. **Modelo E/R**, en la misma revisión que pide ADR-022 (v0.11) y en el mismo encargo: nota de `confirmada` y `fuente`, y fila del catálogo `[MARCA_USUARIO]`.
2. **Arquitectura del Sistema, §16 nº 10 y §4:** retirar la cuestión, corregir la frase que anuncia revisión obligatoria del retenido (D2 bis) y alinear la definición del Nivel 3 con el punto 2.
3. **Plan de Trabajo §9:** fila de ADR-027 en el registro.
