# ADR-020 — Entorno de ejecución del backend y variante de PyTorch

Estado: aprobado

Sustituido por: —

Origen: Decisión conjunta #137 (§B1 y §D), con el acuerdo de L0C84 del 11-nov-2026 23:15 UTC y el cierre de la Issue el 12-nov-2026; #63 (PD-15). El borrador anterior de este ADR (`Estado: propuesto`, `torch` estándar) no llegó a mergearse: este ADR lo completa, no edita un ADR vigente.

Relacionados: #159 (ACO del bloque B, pendiente de número), #117, #134, ADR-019 (#160, pendiente de redactar), ADR-008, ACO-021 (Presidio y MEDDOCAN) y ACO-022 (etiquetado automático).

## Contexto

`backend/pyproject.toml` declara `torch>=2.2,<3.0` sin variante. `backend/Dockerfile` parte de `python:3.12-slim`, instala `".[dev]"`, copia `app/` y `tests/`, y no hornea modelos. En Linux, la instalación estándar de PyTorch desde PyPI arrastra las librerías CUDA de NVIDIA; la imagen resultante del backend pesa **9,66 GB**.

La primera anonimización descarga `es_core_news_sm` y los pesos de MEDDOCAN (unos 508 MB). En ACO-052 esa descarga tardó unos 11 minutos y provocó un timeout (#117).

#134 puso como condición, antes del job E2E, `torch` desde el índice CPU (#63) y los modelos horneados (#117). La decisión conjunta #137 (§B1) aprueba esa configuración y ordena, en su §D, reescribir este ADR para adoptar la variante CPU en lugar de aplazarla.

`tldextract` intenta descargar su lista de sufijos al procesar el primer documento y añade unos 13 s cuando no hay red ni caché (#137 §B1).

El 10-nov-2026 se midió, como evidencia para #63, un experimento conjunto con `torch` desde el índice CPU de PyTorch **y los modelos horneados en la imagen**. La tabla y su atribución están en [el comentario de #63 del 10-nov-2026](https://github.com/ACOMPAS-IA/acompas/issues/63#issuecomment-6781109471); #137 recoge los resultados en §B1.

## Decisión

1. **D1 — Variante y fuente de PyTorch.** `torch>=2.2,<3.0` se instala desde el índice CPU de PyTorch, `https://download.pytorch.org/whl/cpu`, verificado en el spike con `pip install --no-cache-dir torch --index-url` apuntando a ese índice. Es el mismo paquete, pero **una fuente de paquetes nueva**: un cambio de stack que este ADR registra. El índice resolvió `2.15.0+cpu` con ese rango; este ADR lo registra y no fija la versión (ver «Decisiones de implementación»).

2. **D2 — Modelos horneados.** `es_core_news_sm` y MEDDOCAN (`BSC-NLP4BIA/bsc-bio-ehr-es-meddocan`) se incorporan a la imagen durante el build. Ninguna petición los descarga.

3. **D3 — Lista de `tldextract`.** Se hornea la lista de sufijos y el mecanismo queda especificado en #159. Se acepta que la lista se congela hasta el siguiente build.

4. **D4 — Offline.** `HF_HUB_OFFLINE=1` y el equivalente de transformers se fijan en la imagen. Sin la variable no se cumplen ni el arranque offline ni el tiempo de 0,88 s.

5. **D5 — Verificación.** El arranque sin red se comprueba con una `POST /api/anonymization` completa bajo `--network none`, no solo con `build_analyzer()`. Se miden el tamaño del archivo OCI y el tiempo de la primera petición sobre la imagen final (#159); no se confunden con el arranque de `build_analyzer` de la tabla de evidencia.

## Decisiones de implementación

Este ADR no resuelve las decisiones de implementación; #159 las decide y las deja escritas. Aquí quedan fijados los invariantes y los datos de coste para que no se decidan a ciegas:

- fijar la versión exacta de `torch` o mantener el rango registrando la resuelta (`2.15.0+cpu`), porque el índice podría resolver otra versión;
- separar o no la capa de modelos de `COPY app`: hornear detrás de `COPY app` cuesta 115,65 s y 1,01 GB de caché por cada cambio en `app/`;
- si el job de pytest de la CI usa el índice CPU o se deja fuera, con el «motivo escrito» que pide #137 §B1. Este ADR añade el criterio —criterio de este ADR, no transcripción de #137— de que la CI pruebe la misma variante que la imagen o documente la excepción;
- un solo origen para los identificadores de modelo (`Dockerfile` frente a `analyzer.py`), sin decidir aquí cuál.

El comentario del spike (10-nov) dejaba `HF_HUB_OFFLINE`, la caché de `tldextract` y el orden de capas a este ADR. #137 (12-nov), posterior, decide los dos primeros y deja el orden de capas al ACO. Prevalece #137: este ADR no recupera esa decisión.

## Evidencia

Fuente por filas: #137 §B1 (tamaño descomprimido, archivo OCI, carga de modelos, arranque de `build_analyzer` y pytest) y el [comentario de #63 del 10-nov-2026](https://github.com/ACOMPAS-IA/acompas/issues/63#issuecomment-6781109471) (build, primera petición, coste de capa y versión resuelta).

| Métrica | Imagen actual | CPU + modelos horneados |
|---|---:|---:|
| Tamaño descomprimido | 9,66 GB | **3,20 GB** |
| Archivo OCI | no medido | **0,945 GB** (1,108 GB con frontend) |
| Build frío / caliente | — | 359,37 s / 3,34 s |
| Carga de modelos | 8,72 s | **1,39–1,54 s** |
| Arranque de `build_analyzer` (`--network none`) | no medido | 24,53 s sin `HF_HUB_OFFLINE`; **0,88 s** con ella |
| pytest | — | 799 pasan, 20 omitidos |

Los 24,53 s son la imagen nueva, no la actual (#137 §B1). La primera petición offline es otra métrica: 38,23 s sin `HF_HUB_OFFLINE` y 25,23 s con ella en el spike (#63); #159 la mide en la imagen final.

La tabla es de un **experimento conjunto**. El tamaño, el build, la primera petición y el arranque de `build_analyzer` no se atribuyen solo a la variante CPU. La comparación de carga de modelos (8,72 s frente a 1,39–1,54 s) se hizo con los modelos ya en disco en ambas imágenes, así que esa diferencia se atribuye principalmente a CPU. No se midió una imagen CPU sin modelos horneados: el ahorro neto de 6,46 GB es conservador respecto al efecto de retirar CUDA, porque la imagen nueva incluye ~0,5 GB de modelos (caché de HF, 477 MB) que la actual no tiene.

## Alternativas consideradas

- **Mantener `torch` estándar y aplazar la variante CPU (la decisión anterior de este ADR).** Descartada por #137 (§B1 y §D): la configuración CPU es la única medida y la que cumple el umbral de caché de #134.
- **Instalar CPU solo en el `Dockerfile`, sin cambiar la fuente de paquetes.** Descartada: la dependencia declarada y la imagen quedarían divergentes, y el resultado dependería del orden de instalación.
- **Dos ACO separados para la variante de PyTorch y el horneado de modelos (B2 de #137).** Descartada: el estado intermedio no está medido y serían dos fichas y dos revisiones para un `Dockerfile` y un índice.
- **Seguir descargando los modelos en la primera petición.** Descartada: mantiene los ~508 MB, el timeout de ACO-052 y la dependencia de la red en el arranque.

## Consecuencias

- La imagen del backend baja a 3,20 GB y el archivo OCI a 0,945 GB medidos; desaparece la descarga de ~508 MB y la primera petición deja de depender de la red.
- Riesgos registrados: la capa de modelos se invalida con cada cambio en `app/` (115,65 s y ~1 GB por cambio), la lista de `tldextract` se congela hasta el siguiente build y hay que fijar o registrar la versión de `torch`.
- #63 se cierra con este ADR. #117 se cierra con #159, que implementa los cambios.
- Esta PR no cambia `pyproject.toml`, `Dockerfile`, CI ni código: registra la decisión y deja la implementación a #159.
- Sin secretos ni datos reales: los pesos son públicos y las pruebas, sintéticas.
- El registro del Plan de Trabajo §9 se actualiza después del merge, según la Estrategia de actualización documental, y el arnés se regenera con ese cambio (rango y lista de ADR hasta ADR-018 hoy). No se edita a mano.
- El merge de ADR-020 antes que ADR-019 deja un hueco temporal de numeración: es consecuencia del orden que fija #137 §D (cierre de #137 → ADR-020 aprobado → ficha del ACO nuevo), no una autorización de esa §D.

## Fuera de esta decisión

- Implementar los cambios en `Dockerfile`, `pyproject.toml`, CI o código (#159).
- La estrategia E2E, su ADR (ADR-019, #160, pendiente de redactar) y ACO-033.
- Política de anonimización, umbrales y contrato de ACO-024.
- Producción, OCR, frontend y cualquier otro componente.
- La cuestión abierta de la Arquitectura §16 nº 11 (entorno de desarrollo: Docker Compose y VPS): sigue abierta y este ADR no la cierra.

## Documentos afectados

- `docs/adr/ADR-020-entorno-ejecucion-backend-pytorch.md` (este ADR).
- #63 (cierre con el merge), #117 (cierre con #159) y #135 (esta PR).
- Plan de Trabajo §9 (registro de ADR) y regeneración del arnés, después del merge, en el vehículo de #137 («Issue/PR de documentación al actualizar el DO»).
