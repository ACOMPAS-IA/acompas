# Tests de anonimización (Sprint 1)

Estos tests cubren el pipeline de anonimización: detección, política, sustitución, API y no persistencia. La trazabilidad de los criterios T-03, T-04, T-07, T-10, T-13, T-31, T-33, T-34, T-35, T-36, T-37 y T-38 está en [`docs/aco/ACO-026.md`](../../../docs/aco/ACO-026.md), sección 8.1.

## Estructura

| Archivo | Qué cubre | ¿Carga el modelo? |
| --- | --- | --- |
| `test_analyzer.py` | Construcción del analizador y mapeo de MEDDOCAN. | Sí |
| `test_analyzer_warnings.py` | Avisos del analizador sin el texto del documento. | Sí (dos tests) |
| `test_api.py` | Contrato HTTP, errores saneados y nombre de fichero. | No |
| `test_confidence.py` | Fórmula de la confianza del documento. | No |
| `test_config.py` | Umbrales leídos del entorno. | No |
| `test_detection.py` | Detección, asignación de rol y propagación. | Sí |
| `test_no_persistence.py` | No persistencia, logs y contrato de la respuesta. | No |
| `test_policy.py` | Política, umbral de hallazgo y falsos positivos. | No |
| `test_recognizers.py` | Reconocedores de identificadores españoles. | No |
| `test_replacement.py` | Etiquetas, numeración por documento y sustitución. | No |
| `test_service.py` | Servicio, corpus sintético, T-31 y T-34. | Sí (tests de corpus) |

## Cómo ejecutar

### Suite rápida, sin modelo

```bash
pytest tests/anonymization/test_api.py \
  tests/anonymization/test_no_persistence.py \
  tests/anonymization/test_config.py \
  tests/anonymization/test_policy.py \
  tests/anonymization/test_replacement.py \
  tests/anonymization/test_confidence.py \
  tests/anonymization/test_recognizers.py -q
```

No usa red ni servicios externos.

### Tests que necesitan el modelo real

```bash
pytest tests/anonymization/test_analyzer.py \
  tests/anonymization/test_analyzer_warnings.py \
  tests/anonymization/test_detection.py \
  tests/anonymization/test_service.py -q
```

La primera ejecución descarga el modelo MEDDOCAN y el modelo de spaCy en español; las siguientes usan la caché. Los tests de corpus de `test_service.py` reutilizan el fixture de módulo `model_service`, y los de detección el fixture `analyzer` de `test_detection.py`: no se añaden cargas nuevas del modelo.

### Suite completa

```bash
pytest tests/anonymization -q
pytest -q
```

## Contenedor aislado

No uses el contenedor de la demo: su imagen puede ser anterior a la rama y no monta el código. Construye una imagen desde `backend/` y ejecuta con un volumen de caché para no repetir la descarga:

```bash
docker build -t acompas-backend-aco026 backend
docker run --rm -v "$PWD/backend:/app" -w /app \
  -v acompas-aco026-hf-cache:/root/.cache/huggingface \
  acompas-backend-aco026 pytest tests/anonymization -q
```

## CI

`.github/workflows/ci.yml` ejecuta `pytest` en `backend`, sin marcas ni filtros. Por tanto, la CI ejecuta también los tests que cargan MEDDOCAN. ACO-026 no añade cargas nuevas del modelo, pero tampoco puede evitar las que ya existían.

## Datos

Solo se usan los documentos sintéticos de ACO-051 y su manifiesto `expected_entities.json`, a través de `tests.synthetic_data`. No se usan datos reales y el original no se persiste (ADR-005 y ADR-008).
