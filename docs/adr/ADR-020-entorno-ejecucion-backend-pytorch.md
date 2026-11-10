# ADR-020 — Entorno de ejecución del backend y variante de PyTorch

Estado: propuesto

Sustituido por: —

Origen: #63 (PD-15). Documenta la decisión tomada en la PR #5 (ACO-021): usar PyTorch estándar y aplazar la variante solo CPU. Este ADR no cambia esa decisión; la deja registrada en una fuente. La medición de la imagen del backend está en el [comentario de #63 del 10-nov-2026](https://github.com/ACOMPAS-IA/acompas/issues/63#issuecomment-6781109471).

Relacionados: ACO-021 (Presidio + MEDDOCAN), ACO-022 (detección), #43 (hallazgos del analizador), #117 (descarga de modelos), #134 (decisión E2E, fuera de este ADR) y ADR-008 (datos sintéticos).

## Contexto

`backend/pyproject.toml` declara `torch>=2.2,<3.0` sin variante. `backend/Dockerfile` parte de `python:3.12-slim`, instala `".[dev]"`, copia `app/` y `tests/`, y no hornea modelos. En Linux, la instalación estándar de PyTorch desde PyPI arrastra las librerías CUDA de NVIDIA; la imagen resultante del backend pesa **9,66 GB**.

La primera anonimización descarga `es_core_news_sm` y los pesos de MEDDOCAN (unos 508 MB). En ACO-052 esa descarga tardó unos 11 minutos y provocó un timeout (#117).

La decisión de usar PyTorch estándar y aplazar la variante solo CPU se tomó en la PR #5, pero no constaba en ninguna fuente del arnés. #63 recoge ese hueco documental. La revisión propuesta en #63 era un ADR del entorno de desarrollo o una ampliación de la ficha de ACO-022; este ADR elige la primera vía porque la decisión afecta al entorno de ejecución, no a la política de anonimización.

El 10-nov-2026 se midió, como evidencia para #63, una variante de spike con `torch` desde el índice CPU de PyTorch y los modelos horneados en la imagen. Los resultados principales fueron:

| Métrica | Imagen actual | Spike CPU |
|---|---:|---:|
| Tamaño (`docker image inspect`) | 9,66 GB | **3,20 GB** |
| Archivo OCI (`docker save`) | — | **0,945 GB** |
| Build frío / caliente | — | **359,37 s / 3,34 s** |
| Carga de modelos | 8,72 s | **1,39–1,54 s** |
| pytest | — | **799 passed, 20 skipped** |

La medición detectó además tres riesgos: la capa de modelos se invalida con cada cambio en `app/` (build incremental de 115,65 s), el arranque offline necesita `HF_HUB_OFFLINE=1` (24,53 s → 0,88 s) y `tldextract` intenta descargar su lista de sufijos al procesar el primer documento offline (unos 13 s). El detalle y las limitaciones están en el comentario de #63.

Esta evidencia no se adopta en este ADR: cambiar la variante de PyTorch o hornear modelos es una decisión de stack que requiere su propia revisión. El spike no se ha mergeado.

## Decisión

1. **Dependencia (D1-A).** Se mantiene la decisión vigente: `torch` se declara como `torch>=2.2,<3.0` en `backend/pyproject.toml` y se instala desde PyPI, sin fijar la variante CPU ni un índice alternativo. Este ADR no cambia `pyproject.toml`.

2. **Imagen del backend (D2-A).** `backend/Dockerfile` no cambia por este ADR: sigue instalando `".[dev]"` y no hornea modelos. El horneado de modelos es un trabajo distinto, ya recogido en #43 y #117, y no se autoriza aquí.

3. **Registro de la evidencia (D3-A).** La medición de #63 queda como evidencia para una revisión posterior. Cualquier cambio a la variante CPU, al horneado de modelos o a la estrategia de imagen exigirá un ADR o una decisión conjunta propia, según el Plan de Trabajo §8 y §9. Este ADR no autoriza ese cambio.

4. **E2E (D4-A).** La estrategia de los tests E2E y la imagen que usará la CI quedan fuera de esta decisión. Corresponden a la #134 y a su ADR (previsto como ADR-019).

## Alternativas consideradas

- **Mantener PyTorch estándar y documentar el aplazamiento de CPU (elegida).** Es la decisión vigente desde la #5. No cambia el stack ni la imagen y cierra el hueco documental de #63. La evidencia de #63 queda disponible para decidir más adelante.
- **Adoptar ahora `torch` desde el índice CPU.** Descartada en este ADR. La medición es favorable (3,20 GB frente a 9,66 GB), pero cambia la variante de una dependencia del stack y exige su propia decisión; además, quedan por resolver el coste del build incremental, `HF_HUB_OFFLINE` y `tldextract`.
- **Instalar CPU solo en el `Dockerfile`, sin cambiar `pyproject.toml`.** Descartada. La dependencia declarada y la imagen quedarían divergentes, y el resultado dependería del orden de instalación.
- **Hornear los modelos ahora.** Fuera de este ADR. Es un cambio independiente de la variante de PyTorch, con sus propios riesgos de capa y de offline; se sigue en #43 y #117.
- **No documentar nada y dejar #63 abierto.** Descartada. La decisión ya se aplica y la falta de fuente es el problema que #63 debe cerrar.

## Consecuencias

- La decisión sobre PyTorch estándar queda registrada y #63 puede cerrarse cuando este ADR se apruebe y se mergee.
- La imagen del backend sigue en 9,66 GB y la primera anonimización sigue descargando unos 508 MB; #117 y #43 no se cierran con este ADR.
- No se añaden dependencias, no se cambia el `Dockerfile`, no se modifica la CI y no se toca el código.
- La evidencia de #63 queda enlazada para la revisión futura de la variante CPU y para el ADR del E2E.
- El registro del Plan de Trabajo §9 se actualiza después del merge, según la Estrategia de actualización documental. El arnés no se edita a mano.
- No se usan datos reales ni secretos.

## Fuera de esta decisión

- Adoptar la variante CPU de PyTorch o cambiar el índice de instalación.
- Hornear modelos en la imagen, cambiar el `Dockerfile` o modificar la estrategia de caché de la CI.
- La estrategia de los tests E2E, la herramienta, la CI de E2E y la imagen que usará (#134 y su ADR).
- Cambios en la política de anonimización, en ACO-021 o en ACO-022.
- Producción, OCR, frontend y cualquier otro componente del stack.

## Documentos afectados

- `docs/adr/ADR-020-entorno-ejecucion-backend-pytorch.md` (este ADR).
- #63 (cierre después del merge).
- Plan de Trabajo §9 (registro de ADR, después del merge).
