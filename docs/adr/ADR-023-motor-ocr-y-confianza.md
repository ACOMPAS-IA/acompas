# ADR-023 — Motor de OCR, criterio de sustitución, confianza del documento y formatos de entrada

Estado: aprobado

Sustituido por: —

Origen: Issue #191; Arquitectura del Sistema §16 nº 15 (motor de OCR definitivo) y §16 nº 9 (confianza del OCR y umbrales); matriz del Documento Operativo Sprint 2 v0.4 §6, fila «Motor de OCR y su confianza», que asigna el ADR a Miguel y lo deja como dependencia de ACO-035.

Relacionados: ADR-003 (anonimización en tres niveles y Nivel 2), ADR-004 (OCR exclusivamente local), ADR-005 y ADR-012 (el documento original no se persiste), ADR-008 (sin datos reales hasta las salvaguardas), ADR-013 (política y umbrales de la anonimización; documento ilegible); ACO-024 (formato del Sprint 1), ACO-035 (implementación), ACO-036 (Nivel 3), ACO-051 (corpus sintético), #161 (documentos reales en la demo).

## Contexto

El Sprint 1 cierra con `.txt` UTF-8 como único formato de entrada y sin OCR: no hay motor en el código, ni una dependencia de OCR o de PDF en el backend, ni un paquete del sistema en su imagen. La obtención del texto desde un PDF, una imagen o una foto es del Sprint 2 y es lo que enseña el wireframe 3.

Hechos que enmarcan la decisión:

- **ADR-004 decide el OCR local, no su rendimiento.** Fija Tesseract y deja docTR o PaddleOCR como alternativa «si Tesseract no rinde»; la Arquitectura §4 lo repite como «si no rinde lo suficiente», sin decir sobre qué se mide, con qué precisión, en qué tiempo ni quién lo mide. La Arquitectura §16 nº 15 recoge ese hueco como cuestión abierta.
- **La ilegibilidad se detecta hoy por texto vacío.** ADR-013 declara ilegible el documento cuyo texto extraído está vacío y deja **fuera de su decisión** el uso de la confianza del OCR, que la Arquitectura §16 nº 9 mantiene abierta. Un OCR que devuelve texto basura no dispara nada: hay texto, luego hay documento.
- **La interfaz ya anuncia los formatos y ya tiene el estado.** El wireframe 3 admite «PDF, JPG, PNG · máx. 20 MB» y la pantalla 4c tiene mensaje propio para el documento ilegible, distinto del retenido por baja confianza. El estado `ilegible` existe y el texto vacío ya lo produce; lo que falta es el segundo motivo —la confianza del OCR— y los formatos.
- **El original no se persiste y el texto sí se procesa.** ADR-005 obliga a tratar el fichero en memoria o en un volumen efímero y ADR-012 fija que del original no se conserva más que su nombre genérico y su hash; ADR-013 y ACO-024 trabajan sobre el texto extraído, con un tope de 30.000 caracteres.
- **No hay con qué calibrar todavía.** El corpus sintético de ACO-051 son tres documentos en texto plano; no existe ninguna imagen ni ninguna medición de OCR en el proyecto. Los valores de esta decisión son, por tanto, puntos de partida.

## Decisión

1. **Motor y criterio de sustitución.** Tesseract con el paquete de español sigue siendo el motor, y docTR o PaddleOCR no se instalan mientras cumpla. «Rendir» significa superar esta medición, hecha sobre la imagen de ejecución del backend con Tesseract instalado —hoy no lo tiene: la instalación es de ACO-035— y sobre nueve renders sintéticos: los tres documentos de ACO-051, con sus datos identificativos colocados a propósito, en tres formas cada uno —PDF escaneado a 300 ppp, foto y PDF con capa de texto—. El CER y el tiempo se miden **solo en las dos rutas de OCR** (escaneo y foto, seis renders); el PDF con capa de texto es un control de la extracción, no una prueba de Tesseract: si falla, el problema es del extractor y no se sustituye el motor por eso.

   - **Precisión:** tasa de error de caracteres (CER) global ≤ 10 % y CER ≤ 2 % sobre los valores identificativos colocados a propósito. Las dos se cumplen a la vez; si discrepan, manda la de identificativos: un carácter perdido en un nombre o un DNI es una fuga, uno perdido en una palabra clínica es una molestia.
   - **Tiempo:** ≤ 3 segundos por página en arranque en frío —el primer OCR tras levantar el contenedor, con los modelos ya en disco y sin caché de página—.
   - **Idioma:** español; los documentos del proyecto están en español y no se añaden paquetes de otros idiomas sin una necesidad declarada.
   - **Quién mide:** el responsable de ACO-035, y deja la tabla por documento en la PR de calibración. La medición se repite entera si cambia el motor, el paquete de idioma o el preprocesado de imagen.

2. **Sustituto.** Si la medición del punto 1 no se cumple, el motor alternativo es **PaddleOCR**. La Arquitectura §16 nº 15 pide «el motor alternativo», en singular, y ADR-004 autoriza dos; se nombra uno para no pagar dos calibraciones de la misma decisión, sin que sea un juicio sobre el otro. docTR sigue autorizado por ADR-004 y solo se mide si PaddleOCR tampoco cumple. Cambiar de motor no necesita un ADR nuevo —ADR-004 ya lo autoriza—, pero sí repetir la medición y dejarla en la PR que lo cambie.

3. **Confianza del OCR como segundo motivo de ilegibilidad.** La API de Tesseract devuelve, por palabra, un texto y una confianza en una escala de 0 a 100 (`image_to_data`, campo `conf`, con −1 en las palabras sin confianza; https://github.com/madmaze/pytesseract). Es un dato externo al proyecto y se cita como tal. La confianza del documento es la **media de esas confianzas ponderada por longitud**, contando solo las palabras de más de un carácter, y se **normaliza a 0–1** (dividiendo entre 100) para usar la misma escala que los umbrales de ADR-013. Un documento es **ilegible** en dos casos: si no se extrae texto —lo que ya decidía ADR-013— o si esa media normalizada queda por debajo de 0,60.

   - **Mismo estado, sin estado nuevo.** Se reutiliza el estado `ilegible` y su aviso al paciente, distinto del de baja confianza de anonimización: la pantalla 4c ya los separa. Su literal —«El documento no contiene texto que se pueda leer»— deja de encajar con un documento que sí trae texto y no se lee bien; el texto de los avisos está fuera de ADR-013 y sigue abierto, así que este ADR no lo fija.
   - **Los umbrales no se distinguen por nivel.** No hay un valor para el Nivel 2 y otro para el Nivel 3: la decisión alcanza a la extracción del texto, que es anterior a los niveles. El diseño del Nivel 3 es de la Arquitectura §16 nº 10.
   - **No se recalibran con documentos reales** hasta que ADR-008 lo permita. Cambiar el valor no exige un ADR nuevo mientras se respete el criterio: el cambio y su justificación quedan en la PR que lo hace, como en ADR-013.
   - **El 0,85 de ADR-013 no se toca.** Mide la confianza de la anonimización, no la del OCR, y este ADR no reabre ni el umbral de hallazgo ni el de documento.

4. **Formatos de entrada y ruta de extracción.** Se aceptan `.txt` en UTF-8 —sin cambios—, **PDF, JPG y PNG de hasta 20 MB**, que es lo que anuncia el wireframe 3. Cada formato tiene su ruta, y todas son locales:

   - **PDF con capa de texto:** se extrae el texto directamente, sin OCR. Es el caso barato y el más fiel; si esa extracción no devuelve texto, el documento es ilegible y no se reintenta con OCR.
   - **PDF sin capa de texto**, o con menos de 100 caracteres por página: se rasteriza a 300 ppp en memoria y se pasa el OCR página a página.
   - **JPG y PNG:** OCR directo sobre la imagen.
   - Las páginas se concatenan con un salto de línea, sin marcadores ni numeración añadida, para que el texto extraído siga siendo el que se anonimiza y sobre el que se marcan los tramos.
   - **No se conservan metadatos de imagen** (EXIF): no hacen falta para el texto y pueden contener datos del dispositivo o del paciente.
   - **PDF cifrado, fichero corrupto o imagen sin texto:** documento ilegible, con el motivo que ya existe. El original no se persiste en ningún caso (ADR-005, ADR-012).
   - El tope de 30.000 caracteres del contrato de anonimización sigue aguas abajo, sin cambios: el OCR no lo modifica ni lo amplía.

5. **Valores iniciales y su naturaleza.** Los números de los puntos 1, 3 y 4 —10 % y 2 % de CER, 3 s por página, 0,60 de confianza y 100 caracteres por página— son **valores iniciales configurables**, no medidas: ninguna fuente los fija y el proyecto no tiene todavía con qué medirlos. Los calibra ACO-035 con el corpus de ACO-051 y sus renders, y el ADR no se edita para cambiarlos: se cambian en configuración y se justifican en su PR. Los 300 ppp y el español son parte de la ruta y del criterio, no medidas: se cambian con ellos y por el mismo procedimiento. Los que no son numéricos —OCR local, un solo alternativo, dos motivos de ilegibilidad, una ruta por formato— son la decisión y no se calibran.

6. **Librerías.** Este ADR fija la ruta de extracción, no la librería que la implementa: elegir la de PDF o la de imagen añade una dependencia al stack y eso no lo decide un ADR de criterio, sino ACO-035 al ampliar su ficha, que es donde se nombra la dependencia y se autoriza.

## Alternativas consideradas

- **Medir Tesseract, docTR y PaddleOCR a la vez:** descartada. Triplica el trabajo de calibración para una decisión que se resuelve con un sí o un no, y ninguno de los tres está instalado.
- **Confianza por línea en vez de por palabra:** descartada. La línea agrega palabras de relleno y esconde justo la palabra que el OCR no ha sabido leer; el umbral dejaría pasar documentos con un nombre destruido.
- **Seguir detectando la ilegibilidad solo por texto vacío:** descartada por la Arquitectura §16 nº 9. Un OCR que devuelve ruido produce un documento «válido» sin nada que anonimizar.
- **Tratar la baja confianza de OCR como documento retenido:** descartada. El retenido significa «hay datos personales y no me fío de haberlos detectado»; aquí el problema es anterior, y la pantalla 4c ya tiene un mensaje distinto para cada caso.
- **Umbral propio para el Nivel 3:** descartada. El Nivel 3 trabaja sobre texto ya extraído y su diseño es de la Arquitectura §16 nº 10; un umbral por nivel obligaría a decidir dos veces lo mismo.
- **Aceptar solo PDF con capa de texto en la demo:** descartada. Deja fuera la foto y el escaneo, que es el caso real del paciente y lo que el wireframe 3 promete.
- **Rechazar el PDF sin capa y pedir otro fichero:** descartada por el mismo motivo y porque el OCR es la razón de ser del Sprint 2.

## Consecuencias

- ACO-035 implementa el motor, la ruta por formato, la confianza del documento y la calibración. Su ficha recoge los compromisos de esta decisión al ampliarse.
- Los renders sintéticos de los documentos de ACO-051 son fixtures de ACO-035: ACO-051 no cambia ni se amplía, y no se usan documentos reales.
- El estado `ilegible` gana un motivo sin cambiar de nombre, de código de respuesta ni de pantalla; el literal del aviso sigue abierto.
- El Nivel 2 y el Nivel 3 reciben un texto ya validado por OCR; ACO-036 no hereda ninguna decisión de umbral.
- Las librerías de PDF e imagen entran al stack con ACO-035 y con su ficha, no con este ADR.
- La calibración puede mover los cinco valores iniciales; ninguna de esas variaciones reabre ADR-004 ni ADR-013.

## Fuera de esta decisión

- El umbral de confianza de la anonimización y el tratamiento del documento retenido (ADR-013).
- La validación reforzada de entidades y el flujo del Nivel 2 (ACO-035).
- El diseño del Nivel 3 y el documento retenido (Arquitectura §16 nº 10; ACO-036).
- La comprobación de que el documento es de tipo clínico (Arquitectura §16 nº 8).
- El uso de documentos reales en cualquier entorno (ADR-008; #161).
- La elección de librerías de PDF e imagen (ACO-035).
- El texto de los avisos al paciente.

## Documentos afectados

- Arquitectura del Sistema §16 nº 9 y §16 nº 15, que se retiran de la lista de cuestiones abiertas
- Arnés: 03-REGLAS, 05-DISEÑO y 09-TESTS, 04-INTERFAZ (la cuestión de los formatos de subida) y el MANIFIESTO, que dejan de listar las dos cuestiones y la de formatos
- Plan de Trabajo §9, registro de ADR
- ACO-035, que arranca con esta decisión
