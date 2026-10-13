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


## Regeneración (modo B)

Regeneración según la Estrategia de Actualización Documental §4.10 y el Anexo B, modo B, con las reglas del modo A. Fecha: 2026-10-11. Rama: `docs/arnes-regeneracion-adr013`. Fuentes, versiones y commit: `MANIFIESTO.md`.

### B.1 Fuentes cambiadas y piezas regeneradas

| Fuente | Cambio (control de cambios o diff) | Secciones con cambio de contenido |
|---|---|---|
| Plan de Trabajo v0.9 → v0.10 | Ficha de alcance y ficha ejecutable; decisiones delegadas y dependencias nombradas; HALLAZGO y ADVERTENCIA; ADR-013 en el registro; criterios de la demo con los dos umbrales, el documento ilegible y las categorías garantizadas | §4, §9, §11, §13 |
| Arquitectura del Sistema v0.7 → v0.8 | Qué se anonimiza; umbral de hallazgo y umbral de documento; documento retenido e ilegible; etiquetas por rol y genérica de persona; nombre del fichero original; cuestiones 7 a 10 | §4, §11, §14, §16 |
| `docs/adr/` (`2cc2f5a` → `22004f1`) | ADR-013, nuevo y aprobado | — |

Las demás fuentes conservan la versión y el SHA-256 del manifiesto anterior. `docs/aco/` no cambia entre los dos commits.

| Pieza | Regenerada | Motivo (cruce con el MANIFIESTO §4) | Cambios principales |
|---|---|---|---|
| 01-PRODUCTO | No | Sus fuentes no cambian; la Arquitectura §16 nº 1 y nº 6 tampoco | — |
| 02-DOMINIO | Sí | Arquitectura §4; ADR-013 | Etiquetas por rol y genérica; categorías; los dos umbrales; confianza del documento; documento retenido e ilegible; dos discrepancias resueltas por prevalencia (§5) |
| 03-REGLAS | Sí | Arquitectura §4, §11, §14, §16; Plan de Trabajo §4, §9; ADR-013 | R-04, R-13, R-15, R-17 y R-38 actualizadas; nuevas R-44 a R-50 (ADR-013), R-51 (ficha de alcance y ficha ejecutable) y R-52 (decisiones y dependencias delegadas) |
| 04-INTERFAZ | Sí | Arquitectura §4, §11, §14 | Flujo del Sprint 1 con los dos umbrales, el retenido y el ilegible; etiquetas, umbrales y documento retenido por prevalencia frente a UC-05, UC-06 y el wireframe 4 |
| 05-DISEÑO | Sí | Arquitectura §4, §11, §14; ADR-013 | Pipeline del módulo de anonimización; pista B; cuestiones 8 a 10 |
| 06-SEMILLA | Sí | Arquitectura §11; ADR-013 | Valores iniciales configurables de los umbrales; sin nombres de ficheros originales; catálogo de etiquetas |
| 07-INTERCAMBIO | Sí | Arquitectura §4, §11; ADR-013 | Analizador, política y umbrales, etiquetas y DOCUMENTO del documento retenido |
| 08-PLAN | Sí | Plan de Trabajo §4, §9, §11 | D-03 y D-06; ficha de alcance y ficha ejecutable; remisión a 03 para ADR-013 |
| 09-TESTS | Sí | Arquitectura §4, §11; ADR-013; D-03 y D-06 | T-04, T-10, T-28, T-29, T-31 y T-32 actualizadas; nuevas T-33 a T-37; los tests leen los umbrales de la configuración |
| AGENTS.md | Sí | Plan de Trabajo §4, §9 | Ficha ejecutable y BUILD (§3); decisiones delegadas y dependencias nombradas (§5); BLOQUEO, FUERA DE ALCANCE, HALLAZGO y ADVERTENCIA en la PR, y solo BLOQUEO detiene (§6) |

Los identificadores R y T del modo A se conservan, y los nuevos continúan la numeración. 04 y 08 no tienen ADR entre sus fuentes (§4.5): lo que procede de ADR-013 se remite a 03 y 09, salvo en las cuestiones abiertas y en el texto de D-03 y D-06, que reproduce el Plan de Trabajo §11. Las etiquetas de persona siguen la Arquitectura §4: `[PACIENTE]`, `[SANITARIO_n]`, `[FAMILIAR_n]` y `[PERSONA_n]`. `[MÉDICO_n]` solo aparece al citar las discrepancias.

Cuestiones abiertas (MANIFIESTO §5):

- **Salen:** «Valor del umbral de confianza» y «Tratamiento del documento retenido» (los resuelve ADR-013), y «Paso de ficha de alcance a ficha ejecutable» (lo resuelve el Plan de Trabajo v0.10).
- **Entran:**
  - las cuestiones 7 a 10 de la Arquitectura §16;
  - el «Fuera de esta decisión» de ADR-013: el texto de los avisos y el nombre de la etiqueta genérica con el catálogo; los demás puntos coinciden con las cuestiones 7 a 10 o con la fila de reconocedores;
  - dos huecos detectados al derivar 09 (PD-21 y PD-22).
- **Se reformula:** «Identificadores del Sprint 1 y filtros sin enumerar» pasa a ser «Lista concreta de reconocedores, filtros y términos permitidos», porque ADR-013 enumera los reconocedores mínimos de ACO-022 y deja la lista concreta a las fichas.

### B.2 Auditoría (solo piezas regeneradas)

**Ronda 1.** Se comprobaron:

- que no hay versiones fuera del manifiesto;
- que `[MÉDICO_n]` no aparece fuera de las discrepancias;
- que no se cita «T-31 del arnés»;
- que no quedan las cuestiones abiertas que salen;
- que 04 y 08 no citan ADR en el cuerpo;
- la trazabilidad entre R y T en los dos sentidos;
- que no queda redacción de umbral único.

Cambios necesarios aplicados:

1. T-28 y T-29 no cubrían R-51 ni R-52. Se añadieron, y se precisó su comprobación (primer commit con la ficha ampliada; decisiones delegadas dentro de sus límites y anotadas en la PR).
2. R-02 indicaba solo T-02, aunque T-01 la cubre y la trazabilidad inversa ya lo recogía. Venía del modo A. Se corrigió a «T-01, T-02».

**Ronda 2.** Se repitieron las comprobaciones y se revisaron a mano los cambios de 02, 04, 05 y 08. No hizo falta ningún cambio. **La auditoría queda cerrada**:

- 52 reglas (R-01…R-52) y 37 verificaciones (T-01…T-37), todas trazadas en los dos sentidos;
- D-01…D-07 con verificación;
- ninguna pieza detenida.

Criterios de aceptación (§4.9): se cumplen como en el modo A (§6). Las piezas regeneradas mantienen «Objetivo y alcance», «Qué no contiene», «Fuentes» y «Cuestiones abiertas». No incorporan contenido de ramas sin fusionar (la ficha de ACO-022 de la PR #47 no se ha leído como fuente) y no convierten cuestiones abiertas en reglas: los valores 0,35 y 0,85 los fija ADR-013 como valores iniciales configurables, y los tests no los fijan.

### B.3 Pendientes del modo A que cierran las fuentes

| Nº | Situación |
|---|---|
| PD-05 | La decisión la toma ADR-013. Queda alinear los documentos derivados: PD-16, PD-17 y PD-18 |
| PD-09 | Cerrado por el Plan de Trabajo v0.10 §4 (ficha de alcance y ficha ejecutable). Recogido en AGENTS.md §3, 03 R-51 y 08 §5 |
| PD-10 | Cerrado por el Plan de Trabajo v0.10 §4: HALLAZGO, ADVERTENCIA y decisiones delegadas, recogidos en AGENTS.md §5 y §6. La regla de prioridad ante situaciones ambiguas y el registro del baseline de git siguen sin fuente y no pasan a AGENTS.md |
| PD-14 | Cerrado por el Plan de Trabajo v0.10 §4 (dependencias nombradas por la ficha). Recogido en AGENTS.md §5 y 03 R-52. Ver PD-20 |

PD-04 se aplicó: las tablas de entidades del Modelo E/R se volvieron a leer del .docx v0.9, cuyo SHA-256 no cambia.

### B.4 Pendientes nuevos

Se proponen con la etiqueta «pendiente documental», igual que en §4. Las Issues no se han creado. Ninguno bloquea el arnés.

| Nº | Documento afectado | Descripción | Tipo | Revisión propuesta |
|---|---|---|---|---|
| PD-16 | Modelo E/R | TIPO_ETIQUETA usa `[MÉDICO]` como ejemplo, y ETIQUETA_ANONIMIZACION usa `[MÉDICO_1]` en `numero` y `'MEDICO'` en `tipo_entidad`, frente a las etiquetas de la Arquitectura §4 (`[SANITARIO_n]`, `[FAMILIAR_n]`, `[PERSONA_n]`). DOCUMENTO dice que el documento retenido se guarda «para revisión posterior», con el estado `retenido_baja_confianza`, frente a ADR-013 (no se guarda; solo queda un registro de auditoría). | Discrepancia con un ADR y con la Arquitectura (prevalecen las fuentes normativas; 02-DOMINIO §5) | Pasada B, paso 6 |
| PD-17 | Casos de Uso | UC-05 usa `[MÉDICO_1]`. UC-06 habla de un único umbral de confianza y de que el documento retenido «se retiene para que lo revise el paciente», frente a ADR-013. No recoge el documento ilegible. | Discrepancia con un ADR y con la Arquitectura | Pasada B |
| PD-18 | Wireframes, pantalla 4 | Muestra `[MÉDICO_1]` y `MÉDICO_2`, y un único «umbral mínimo: 0.85». No tiene el aviso de documento retenido ni el de documento ilegible. **Precisión:** el wireframe 4 no dice literalmente «revisión posterior» («se habría retenido… en vez de mostrarse aquí»), así que lo que choca con ADR-013 son las etiquetas, el umbral único y la falta de los avisos. | Discrepancia con un ADR y con la Arquitectura | Pasada B, paso 5 |
| PD-19 | ADR-013 | Las Consecuencias citan «T-31 del arnés», y la Estrategia §4.1 prohíbe que un ADR cite archivos del arnés. No es una contradicción de contenido, y las piezas no lo citan. Un ADR aprobado no se edita, así que la referencia solo puede retirarse cuando se sustituya ADR-013. Mientras tanto, el arnés conserva el identificador T-31 para la comprobación de fugas. | Referencia prohibida | Cuando se sustituya ADR-013 |
| PD-20 | Plan de Trabajo §8 | §8 exige una decisión conjunta para «nuevas dependencias», sin mencionar la excepción de §4 (una dependencia que nombra la ficha ejecutable queda autorizada por su revisión). AGENTS.md y 03 (R-38, R-52) recogen las dos reglas con su sección, y la excepción la declara la propia §4 («el agente no se bloquea»). Conviene que §8 remita a §4. | Incoherencia de redacción | Siguiente revisión del Plan de Trabajo |
| PD-21 | Ficha de ACO-051 o de ACO-026 | T-31 comprueba solo las categorías garantizadas, pero el manifiesto de ACO-051 no las distingue: `DATE_TIME` incluye la fecha de nacimiento y las demás fechas, y `TERRITORIO` incluye la localidad y la provincia, que ADR-013 no menciona. Falta definir cómo se identifican las entidades que comprueba T-31. | Hueco (cuestión abierta en 09) | Ficha de ACO-026 al ampliarse (ADR-013 la cita entre las afectadas) o revisión de ACO-051 |
| PD-22 | Ficha de ACO-023 / Plan de Trabajo | ADR-013 exige un registro de auditoría del documento retenido (fecha, tipo de documento, motivo). El modelo del registro de auditoría está abierto (Arquitectura §16 nº 4) y la auditoría completa queda fuera del Sprint 1, así que no está definido qué registro debe quedar en el Sprint 1. | Hueco (cuestión abierta en 09) | Ficha de ACO-023 al ampliarse |
| PD-23 | Plan de Trabajo §4 → AGENTS.md | De lo que pedía PD-10 quedan sin fuente, y por tanto fuera de AGENTS.md, la regla de prioridad ante ambigüedades y el registro del baseline de git. Si se quieren en AGENTS.md, hay que llevarlos antes al Plan de Trabajo §4. | Cambio de gobernanza a decidir | Plan de Trabajo v0.11, junto con PD-20 |

### B.5 Hallazgos que no requieren cambios

- **Etiquetas en ADR-013 y en la Arquitectura.** Las Consecuencias de ADR-013 dicen que la Arquitectura y los wireframes «mantienen» `[MÉDICO_1]`, pero la Arquitectura v0.8 usa `[SANITARIO_1]`. ADR-013 deja fuera de la decisión el nombre exacto de las etiquetas, así que no hay contradicción. El arnés sigue la Arquitectura §4, como indica el encargo.
- **Umbral único en la Arquitectura §4 (último párrafo) y §15.** Siguen hablando de un «umbral conservador» o «umbral de confianza». Es compatible con el umbral de documento. Conviene ajustar la redacción en la siguiente revisión.
- **Fichas de alcance de ACO-022, 023 y 026, y título de ACO-023 en la matriz** («Umbral de confianza»). Están en singular, pero ADR-013 prevé actualizar esas fichas al ampliarlas. No contradicen la política: la remisión de 08 §5 a 03 lo cubre.
- **`ADR-013.md` suelto en `~/projects/acompas-fuentes/`.** Difiere del fichero de `docs/adr/` en una consecuencia: el acierto de rol se mide «sobre el mismo corpus» frente a «con casos sintéticos definidos en la ficha de ACO-022». La fuente es la del repositorio (MANIFIESTO §2).

### B.6 Verificación de integridad

- Rama `docs/arnes-regeneracion-adr013`, HEAD = `22004f1cebee17787826e2cbec8107e6a320e99e` antes del commit, sin cambios previos.
- Solo cambian `AGENTS.md`, `docs/arnes/02` a `09`, `MANIFIESTO.md` y este informe. `01-PRODUCTO.md`, `docs/adr/`, `docs/aco/` y el código no cambian.
- `~/projects/acompas-fuentes`: los SHA-256 coinciden antes y después de la regeneración.
