# INFORME DE GENERACIÓN DEL ARNÉS

Primera generación (modo A) según la Estrategia de Actualización Documental §4 y el Anexo B. Fuentes, versiones y commit: `MANIFIESTO.md`.

## 1. Resumen

| Paso (Anexo B) | Resultado |
|---|---|
| 1. Condiciones previas (§4.3) | Se cumplen las tres (ver MANIFIESTO §3) |
| 2. Generación de las piezas (§4.5, §4.1, §4.6) | 01–09 en `docs/arnes/` y `AGENTS.md` en la raíz. **Ninguna pieza detenida** |
| 3. Manifiesto (§4.2) | `docs/arnes/MANIFIESTO.md` |
| 4. Auditoría (§4.4) | Dos rondas. Cerrada: los cambios de la segunda ronda se aplicaron y lo que queda abierto pasa a pendientes (§4) |
| 5. Criterios de aceptación (§4.9) | Se cumplen (§6) |
| Calibración (ejecución de un ACO con el arnés) | ACO-021 repetido en un worktree desechable. Dos hallazgos sobre el arnés, que pasan a pendientes (§8) |

No se ha modificado ninguna fuente. Los SHA-256 de `~/projects/acompas-fuentes` coinciden antes y después, y en git solo cambian `AGENTS.md` (sustituido) y `docs/arnes/` (nuevo). El resultado se sube en la rama `docs/arnes-primera-generacion` para su revisión en PR.

## 2. Decisiones del usuario tomadas en el PLAN

| Tema | Decisión |
|---|---|
| Las tablas de entidades del Modelo E/R en .md perdieron las columnas Tipo, Restricción y Descripción | Se leen del .docx de la misma versión (constan en el MANIFIESTO) |
| Los Wireframes muestran nombres de fichero originales, frente a ADR-012 | Prevalece la fuente normativa (Estrategia §9 y §4.6). 04 se genera y la discrepancia pasa a pendientes |
| Documento retenido: UC-06, el wireframe 4 y el ADR pendiente no coinciden | Cuestión abierta, no contradicción. Las piezas solo fijan «se retiene y no se carga» |

Con el mismo criterio de prevalencia se trató la discrepancia de los estados de ENTRADA_GLOSARIO (Modelo E/R frente a Arquitectura).

## 3. Auditoría

### Ronda 1

Se revisaron las contradicciones, los huecos, las referencias obsoletas y los desajustes entre reglas y tests. Comprobaciones automáticas: versiones fuera del manifiesto, citas fuera de las fuentes de cada pieza (§4.5), secciones obligatorias y trazabilidad entre R y T en los dos sentidos.

Cambios necesarios aplicados:

1. Algunas piezas citaban en el cuerpo fuentes que la §4.5 no les asigna: 01 citaba ADR; 03 y 05 citaban el Documento Operativo; 04 citaba ADR, el Plan de Trabajo y fichas. Se sustituyeron por la cita a la fuente propia de la pieza o por una remisión a la pieza correspondiente. Se fijó la convención de que las cuestiones abiertas sí pueden citar la fuente donde constan como abiertas (MANIFIESTO §4).
2. Los criterios de la demo, cuya fuente es el Plan de Trabajo, no son fuente de 09. Pasan a 08-PLAN como D-01…D-07, y 09 los verifica por remisión.
3. Las cabeceras de fuentes de 01, 02, 03, 04, 05, 07, 08 y 09 se alinearon con las secciones citadas realmente y con el manifiesto.
4. En 04, la asignación de partes de pantalla al Sprint 1 se marcó como inferencia.

Trazabilidad tras la ronda: las 43 reglas (R-01…R-43) tienen al menos una verificación, las 32 verificaciones (T-01…T-32) cubren una regla o un criterio de la demo, y D-01…D-07 tienen verificación. No hay versiones fuera del manifiesto.

### Ronda 2

Se repitieron las comprobaciones. Solo hizo falta un cambio: en 04, una remisión desactualizada tras mover los criterios de la demo («criterios de la demo, en 09-TESTS» pasa a «en 08-PLAN, y su verificación, en 09-TESTS»). Aplicado. **La auditoría queda cerrada**: lo restante no requiere cambiar el arnés, sino las fuentes, y pasa a la lista de pendientes.

## 4. Lista de pendientes documentales

Las Issues **no se han creado**; se crearán cuando se apruebe la PR del arnés. Se proponen con la etiqueta «pendiente documental» (regla 4 de la Estrategia), indicando el documento afectado y la revisión planificada en que se resuelven. Ninguna bloquea el arnés.

| Nº | Documento afectado | Descripción | Tipo | Revisión propuesta |
|---|---|---|---|---|
| PD-01 | Wireframes MVP | Las pantallas 2, 4 y 5 muestran nombres de fichero originales («analitica_junio.pdf», «informe_patologia.pdf»…), frente a ADR-012 (nombre genérico). Falta además el aviso de documento duplicado. | Discrepancia con un ADR (prevalece ADR-012) | Pasada B, paso 5 (amplía el paso previsto para el aviso de duplicado) |
| PD-02 | Modelo E/R | Los estados de ENTRADA_GLOSARIO (`pendiente_de_validacion`, `consolidada`) no coinciden con la Arquitectura §6 y §9 (pendiente, validada). | Discrepancia con la Arquitectura (prevalece la Arquitectura) | Pasada B, paso 6 |
| PD-03 | Modelo E/R | La nota de ETIQUETA_ANONIMIZACION mantiene «posicion_fin… (decisión confirmada)», mientras que las descripciones de los campos y el control de cambios la dan como cuestión abierta. | Incoherencia interna | Pasada B, paso 6 |
| PD-04 | Modelo E/R (exportación a .md) | La conversión a Markdown pierde las columnas Tipo, Restricción y Descripción. En la próxima regeneración del arnés las tablas tendrían que volver a leerse del .docx. | ADVERTENCIA de proceso | Antes de la siguiente regeneración |
| PD-05 | Plan de Trabajo (ADR pendiente) → Casos de Uso, Wireframes y Modelo E/R | Tratamiento del documento retenido: UC-06 («para que lo revise el paciente»), el wireframe 4 («en vez de mostrarse») y el Modelo E/R («revisión posterior», `retenido_baja_confianza`) adelantan aspectos de una decisión que el Plan de Trabajo §9 tiene pendiente de ADR (ACO-023). Además, revisar un documento retenido parece chocar con que el original no se persiste (ADR-005): es una **inferencia** que debe valorar el ADR. | Decisión pendiente | ADR del Sprint 1 (ACO-023); después, alinear los documentos derivados |
| PD-06 | Modelo E/R o Wireframes | El wireframe 8 pide un «Motivo (opcional)» que no existe en SOLICITUD_DESBLOQUEO_CREDITO. | Hueco | Pasada B (paso 5 o 6), por decisión de producto |
| PD-07 | Fichas ACO-020, 024 y 032 / Documento Operativo | No está definido qué formato acepta la interfaz mínima del Sprint 1: el wireframe 3 admite PDF, JPG y PNG, pero el pipeline del Sprint 1 trabaja sobre texto. | Hueco que afecta al Sprint 1 | Ficha de ACO-024 o de ACO-032, al ampliarse |
| PD-08 | Documento Operativo Sprint 1 | La matriz hace depender ACO-014 de «007», que no tiene ficha en docs/aco/. | Hueco | Cierre del Sprint 1 o siguiente revisión |
| PD-09 | Plan de Trabajo | El procedimiento para pasar de ficha de alcance a ficha ejecutable (puntos a confirmar y aclaraciones del responsable, confirmados en la revisión de la PR) solo existe en `docs/aco/PLANTILLA.md`, que no es fuente. | Hueco de gobernanza | Siguiente revisión del Plan de Trabajo |
| PD-10 | Plan de Trabajo | El AGENTS.md anterior tenía reglas que **no tienen fuente** en el Plan de Trabajo y, por tanto, no pasan al arnés: las categorías HALLAZGO y ADVERTENCIA, las decisiones técnicas delegadas por la ficha, la separación entre decisión delegada y hallazgos, la regla de prioridad ante situaciones ambiguas y el registro del baseline de git durante PLAN (integridad del repositorio). Si el equipo quiere conservarlas, deben incorporarse al Plan de Trabajo §4 y regenerar AGENTS.md. | Cambio de gobernanza a decidir | Siguiente revisión del Plan de Trabajo |
| PD-11 | Repositorio / Plan de Trabajo | El Plan de Trabajo §4 y AGENTS.md remiten a la «Guía rápida de revisión de PR», que no está en el repositorio. | Referencia sin destino | Siguiente revisión del Plan de Trabajo |
| PD-12 | Plan de Proyecto | El riesgo «Concentración de carga en una persona» atribuye al Plan de Trabajo la mitigación (recortar ACO-052 y aplazar parte de ACO-026), pero esa mitigación está en el Documento Operativo §9. | Referencia obsoleta | Pasada B, paso 3 |
| PD-13 | Modelo E/R | FRAGMENTO_RAG.embedding fija VECTOR(768), cuando el modelo de embeddings y la dimensionalidad siguen pendientes (ADR-007, Plan de Trabajo §9). | Detalle adelantado a una decisión abierta | Pasada B, paso 6 (marcarlo como provisional) |
| PD-14 | Plan de Trabajo §8 → AGENTS.md | En la calibración, el agente declaró BLOQUEO por el modelo de spaCy que necesita MEDDOCAN, aunque la ficha de ACO-021 incluye «las dependencias necesarias para utilizar Presidio Analyzer y el motor NLP requerido». La regla de que una dependencia nueva es BLOQUEO no distingue las que autoriza la propia ficha. | Sobrebloqueo (hallazgo de calibración) | Siguiente revisión del Plan de Trabajo; después, regenerar AGENTS.md |
| PD-15 | Ficha de ACO-021 o ADR del entorno de desarrollo | La decisión de usar PyTorch estándar y aplazar la variante solo CPU (tomada en la #5) no consta en ninguna fuente del arnés; en la calibración hubo que darla de palabra. Está relacionada con el tamaño de la imagen del backend (9,66 GB). | Decisión sin fuente (hallazgo de calibración) | ADR del entorno de desarrollo (Plan de Trabajo §9) o ampliación de la ficha de ACO-022 |

Ya previstos en la pasada B, y sin Issue nueva: integrar en la Arquitectura §16 los ADR pendientes del Sprint 1 del Plan de Trabajo §9, y retirar la referencia a la «Propuesta de Plan de Trabajo» (paso 1); el Documento Operativo duplica la Definition of Done del Plan de Trabajo, con criterios adicionales no contradictorios (paso 4; 08-PLAN recoge la unión de ambas).

## 5. Hallazgos que no requieren cambios

- **Lista blanca y email:** ADR-001 y la Arquitectura §11 dicen que ACOMPAS nunca almacena el email del paciente, pero EMAIL_AUTORIZADO guarda emails autorizados antes del registro. ADR-009 lo decide de forma explícita (sin referencia al UUID), así que no es contradicción. El arnés lo recoge así en 02, 03 y 07. Convendría aclarar la redacción de la Arquitectura en su siguiente revisión.
- **Nivel 3, ¿confirmación u opción?:** UC-20 dice, en las relaciones, que «el paciente confirma el resultado», y la Arquitectura y el wireframe 4 lo presentan como opcional. Es compatible («No he encontrado nada más» funciona como confirmación opcional), y es posterior al Sprint 1.
- **Fichas con datos de la matriz:** ACO-021 §6 repite su dependencia, que coincide con la matriz. Es una duplicación tolerada (regla 5).

## 6. Criterios de aceptación (§4.9)

| Criterio | Comprobación | Resultado |
|---|---|---|
| Las piezas 01–09 y AGENTS.md tienen un objetivo y un alcance inequívocos | Cada pieza abre con «Objetivo y alcance» y «Qué no contiene» (comprobado automáticamente) | Cumple |
| Cada pieza identifica sus fuentes normativas y derivadas, y el manifiesto registra sus versiones exactas | Sección «Fuentes» en cada pieza; MANIFIESTO §2 y §4 | Cumple |
| No se incorporan documentos antiguos ni decisiones nuevas | Solo las fuentes congeladas; ninguna versión fuera del manifiesto; las inferencias están marcadas (04 §2, 06 §2 y las cuestiones abiertas de 06); las reglas del AGENTS.md anterior sin fuente se retiraron (PD-10) | Cumple |
| Las cuestiones abiertas no se convierten en requisitos | Umbral, documento retenido, gateway, secretos, formato de entrada, D9 y demás están en «Cuestiones abiertas» y en MANIFIESTO §5; los tests no fijan valores (09) | Cumple |
| Los ACO pueden ejecutarse sin reconstruir decisiones del proyecto | 08 da orden, matriz, alcance y estado por ACO; 03 y 09 dan reglas y verificaciones; AGENTS.md da el comportamiento. Lo que falta está identificado como cuestión abierta, y AGENTS.md lo convierte en BLOQUEO cuando impide ejecutar | Cumple, con las cuestiones abiertas de MANIFIESTO §5 |

## 7. Verificación de integridad

Estado del repositorio al terminar la generación, antes del commit de esta PR.

- Antes y después: rama `docs/arnes-primera-generacion`, HEAD = `2cc2f5ac92413f88b5275e8b7964a8845a12b6d6`, sin cambios staged.
- `git status --porcelain` final: `M AGENTS.md` y `?? docs/arnes/`. Sin cambios en `docs/adr/`, `docs/aco/` ni en el código.
- `~/projects/acompas-fuentes`: los SHA-256 de todos los ficheros coinciden antes y después de la generación.

## 8. Calibración con ACO-021

Antes de la revisión en PR, el arnés se probó ejecutando con él un ACO ya implementado, para comparar el resultado con lo fusionado. Los fallos del arnés se corrigen en sus fuentes y regenerando, no editando las piezas.

### 8.1 Planteamiento

- **ACO:** ACO-021 (Presidio + MEDDOCAN), implementado en `main` por la PR #5.
- **Entorno:** worktree desechable `~/projects/calib-aco021`, rama local `calib/aco-021` desde el commit anterior a la #5 (`a15bc9f^1`), con el arnés nuevo (sin este informe), la ficha actual de ACO-021 y los ADR vigentes.
- **Bloqueos del agente:** declaró BLOQUEO por el mapeo de MEDDOCAN, el modelo de spaCy, PyTorch y la CI. Se respondieron con las decisiones que tomó la #5 (PyTorch estándar, sin tocar el Dockerfile ni la CI).
- **Resultado:** implementación commiteada en `calib/aco-021`; 14 tests pasan en Docker.

### 8.2 Hallazgos sobre el arnés

| Nº | Hallazgo | Tratamiento |
|---|---|---|
| H-01 | Sobrebloqueo por el modelo de spaCy: la ficha ya autoriza las dependencias del motor NLP. | PD-14 |
| H-02 | La decisión sobre PyTorch (estándar, aplazar la variante solo CPU) no tiene fuente en el arnés. | PD-15 |

El resto de bloqueos (mapeo de MEDDOCAN, CI) eran legítimos: son decisiones que la ficha no fija.

### 8.3 Comparación con la PR #5

| Aspecto | PR #5 (en `main`) | Calibración |
|---|---|---|
| Mapeo MEDDOCAN → Presidio | Paciente, sanitarios y familiares a `PERSON` | El mismo |
| `DEFAULT_ENTITIES` | Fija qué se anonimiza e incluye `ES_DNI`, sin reconocedor que lo emita | Eliminado |
| `MIN_SCORE_THRESHOLD` | Definido (0,35) y sin usar | Eliminado |
| Reconocedores registrados | Los predefinidos de Presidio, además de MEDDOCAN | Solo MEDDOCAN |
| Modelo de spaCy | No fijado en dependencias | `es_core_news_sm` fijado en `pyproject.toml` |
| `aggregation_strategy` / `alignment_mode` | `simple` / `expand` | No fijados (valores por defecto) |

La calibración se ajusta mejor al alcance de la ficha (sin política ni umbral, que son de ACO-023). Sobre el código de la #5 se observa además:

- Al agrupar a todas las personas en `PERSON` se pierden las etiquetas por rol ([PACIENTE], [MÉDICO_n]) que usan la Arquitectura §4 y ADR-012.
- Con los reconocedores predefinidos de Presidio registrados, los tests de la #5 podrían pasar gracias a ellos y no a MEDDOCAN.

**Decisión:** el código de la #5 no se corrige con una PR aparte; lo corrige ACO-022. La política de anonimización, el umbral y las etiquetas por rol se proponen en un ADR propio (ADR-013).

### 8.4 Hallazgos de producto (para ACO-022 y ACO-023)

- Un DNI se detectó como persona (puntuación 0,80): hace falta un reconocedor de DNI con letra de control.
- El número de historia clínica no se detectó: hace falta un reconocedor por contexto.
- Algunos fragmentos salen mal delimitados (entidades cortadas o ampliadas).
- La imagen Docker del backend ocupa 9,66 GB (relacionado con PD-15).
- No se comprobó la ejecución en la CI.

### 8.5 Siguiente paso

Calibración con ACO-022, una vez aprobado ADR-013 y ampliada su ficha.

