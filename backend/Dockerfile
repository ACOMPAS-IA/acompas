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

# 1. PyTorch, variante CPU: solo esa pieza, con el rango de `pyproject.toml` y
#    solo desde su índice.
RUN pip install --no-deps --report /tmp/torch-report.json \
        "torch>=2.2,<3.0" --index-url https://download.pytorch.org/whl/cpu

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


def urls(path):
    with open(path, encoding="utf-8") as f:
        informe = json.load(f)
    return [
        item["download_info"]["url"]
        for item in informe.get("install", [])
        if (item.get("download_info") or {}).get("url")
    ]


def es_indice_cpu(url):
    # El índice sirve los ficheros desde su CDN (`download-r2.pytorch.org`),
    # pero la ruta es la del índice CPU: no basta con mirar el host, porque
    # `download.pytorch.org/whl/cu132` es el índice de CUDA.
    partes = urlparse(url)
    host = partes.hostname or ""
    return host.endswith("pytorch.org") and partes.path.startswith("/whl/cpu/")


torch_urls = urls("/tmp/torch-report.json")
deps_urls = urls("/tmp/deps-report.json")
nvidia = sorted(
    dist.metadata["Name"]
    for dist in metadata.distributions()
    if dist.metadata["Name"] and dist.metadata["Name"].lower().startswith("nvidia")
)

print(
    "origen de torch:",
    sorted({urlparse(url).hostname or "(local)" for url in torch_urls}),
)
print(
    "origen del resto:",
    sorted({urlparse(url).hostname or "(local)" for url in deps_urls}),
)
print("paquetes de NVIDIA:", nvidia)

import torch  # noqa: E402

if not torch_urls or not all(es_indice_cpu(url) for url in torch_urls):
    sys.exit("torch no se resolvió solo desde el índice CPU")
if any((urlparse(url).hostname or "").endswith("pytorch.org") for url in deps_urls):
    sys.exit("algún paquete se resolvió desde el índice de PyTorch")
if nvidia:
    sys.exit("la imagen CPU instaló paquetes de NVIDIA")
if torch.version.cuda is not None:
    sys.exit("torch no es la variante CPU")
PY

# 3. Modelos y lista de sufijos, antes de copiar la aplicación. Los nombres
#    salen de `model_ids.py`, que es su origen único.
COPY app/services/anonymization/model_ids.py /tmp/model_ids.py
RUN PYTHONPATH=/tmp python - <<'PY'
import importlib.metadata as metadata
import subprocess
import sys
from pathlib import Path

import torch
from huggingface_hub import hf_hub_download
from model_ids import MEDDOCAN_MODEL, SPACY_MODEL

subprocess.run(
    [sys.executable, "-m", "spacy", "download", SPACY_MODEL],
    check=True,
)

from transformers import AutoModelForTokenClassification, AutoTokenizer  # noqa: E402

# Solo `config.json`: `snapshot_download` traería el repositorio entero, con el
# mismo modelo en dos formatos y casi un giga de más. La ruta del fichero
# termina en el commit resuelto.
ruta_config = Path(hf_hub_download(MEDDOCAN_MODEL, "config.json"))
AutoTokenizer.from_pretrained(MEDDOCAN_MODEL)
AutoModelForTokenClassification.from_pretrained(MEDDOCAN_MODEL)

# La lista de sufijos de tldextract es una dependencia transitiva de Presidio:
# sin ella, analizar un correo sin red intenta descargarla.
import tldextract  # noqa: E402

tldextract.extract("https://example.com")

# Las versiones resueltas quedan dentro de la imagen y en el registro del build:
# el ADR-020 deja abierto fijarlas, pero exige poder saber cuáles son.
versiones = {
    "torch": torch.__version__,
    SPACY_MODEL: metadata.version(SPACY_MODEL.replace("_", "-")),
    MEDDOCAN_MODEL: ruta_config.parent.name,
}
with open("/opt/hf/BUILD-VERSIONS.txt", "w", encoding="utf-8") as archivo:
    for nombre, version in versiones.items():
        archivo.write(f"{nombre}={version}\n")
print("versiones horneadas:", versiones)
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
