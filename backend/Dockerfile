# syntax=docker/dockerfile:1
#
# Imagen del backend de ACOMPAS (ACO-034).
#
# Tres reglas que no se deben deshacer, y por qué:
#
# 1. `torch` se instala aparte, sin dependencias y solo desde el índice CPU de
#    PyTorch, con `--index-url` acotado a esa instalación. Nunca
#    `--extra-index-url`: dejaría que cualquier paquete se resolviera desde ahí
#    (ADR-020 D1). `--no-deps` evita además que ese índice sirva las
#    dependencias de torch, que llegan desde PyPI en el paso siguiente.
# 2. Los modelos y la lista de sufijos se hornean antes de `COPY app`, para que
#    un cambio en la aplicación no los reconstruya (ADR-020, orden de capas).
# 3. Con `HF_HUB_OFFLINE` y `TRANSFORMERS_OFFLINE` fijados, el arranque y la
#    primera anonimización no descargan nada (ADR-020 D4).

FROM python:3.12-slim

# El CDN de xet no está disponible en todas las redes de construcción: sin
# desactivarlo, la descarga de MEDDOCAN falla con `ConnectionError` contra
# `us.aws.cdn.hf.co`. Con él, la descarga va por huggingface.co.
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf \
    TLDEXTRACT_CACHE=/opt/tldextract \
    HF_HUB_DISABLE_XET=1

WORKDIR /app

# 1. PyTorch, variante CPU: solo esa pieza y solo desde su índice.
RUN pip install --no-deps --report /tmp/torch-report.json \
        torch --index-url https://download.pytorch.org/whl/cpu

# 2. El resto, desde PyPI. Se comprueba el informe de pip y las versiones
#    instaladas: un paquete resuelto fuera de PyPI, o cualquier rastro de
#    NVIDIA, rompe la construcción.
COPY pyproject.toml .
RUN pip install --report /tmp/deps-report.json ".[dev]" \
 && python - <<'PY'
import importlib.metadata as metadata
import json
import sys
from urllib.parse import urlparse


def origenes(path):
    with open(path, encoding="utf-8") as f:
        informe = json.load(f)
    hosts = set()
    for item in informe.get("install", []):
        url = (item.get("download_info") or {}).get("url")
        host = urlparse(url).hostname if url else None
        if host:
            hosts.add(host)
    return hosts


def es_indice_pytorch(host):
    # El índice sirve los ficheros desde su CDN (`download-r2.pytorch.org`).
    return host == "download.pytorch.org" or host.endswith(".pytorch.org")


torch_hosts = origenes("/tmp/torch-report.json")
deps_hosts = origenes("/tmp/deps-report.json")
nvidia = sorted(
    dist.metadata["Name"]
    for dist in metadata.distributions()
    if dist.metadata["Name"] and dist.metadata["Name"].lower().startswith("nvidia")
)

print("origen de torch:", sorted(torch_hosts))
print("origen del resto:", sorted(deps_hosts))
print("paquetes de NVIDIA:", nvidia)

import torch  # noqa: E402

if not torch_hosts or not all(es_indice_pytorch(host) for host in torch_hosts):
    sys.exit("torch no se resolvió solo desde el índice CPU")
if any(es_indice_pytorch(host) for host in deps_hosts):
    sys.exit("algún paquete se resolvió desde el índice CPU de PyTorch")
if nvidia:
    sys.exit("la imagen CPU instaló paquetes de NVIDIA")
if torch.version.cuda is not None:
    sys.exit("torch no es la variante CPU")
PY

# 3. Modelos y lista de sufijos, antes de copiar la aplicación. Los nombres
#    salen de `model_ids.py`, que es su origen único.
COPY app/services/anonymization/model_ids.py /tmp/model_ids.py
RUN PYTHONPATH=/tmp python - <<'PY'
import subprocess
import sys

from model_ids import MEDDOCAN_MODEL, SPACY_MODEL

subprocess.run(
    [sys.executable, "-m", "spacy", "download", SPACY_MODEL],
    check=True,
)

from transformers import AutoModelForTokenClassification, AutoTokenizer  # noqa: E402

AutoTokenizer.from_pretrained(MEDDOCAN_MODEL)
AutoModelForTokenClassification.from_pretrained(MEDDOCAN_MODEL)

# La lista de sufijos de tldextract es una dependencia transitiva de Presidio:
# sin ella, analizar un correo sin red intenta descargarla.
import tldextract  # noqa: E402

tldextract.extract("https://example.com")
PY

# A partir de aquí, el modelo no puede descargar nada (ADR-020 D4).
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

COPY app ./app
COPY tests ./tests

# 4. Comprobación: el analizador se construye y analiza dentro de la imagen. Si
#    algo no viaja en ella, la construcción falla.
RUN python -c "from app.services.anonymization.analyzer import build_analyzer; \
a = build_analyzer(); \
print(sorted({r.entity_type for r in a.analyze(text='correo ana@example.com', language='es')}))"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
