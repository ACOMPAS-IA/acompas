"""Identificadores de los modelos de anonimización.

Origen único (ACO-034; ADR-020, decisiones de implementación): el build de la
imagen hornea exactamente estos modelos y el analizador carga los mismos. No
dupliques los nombres en el `Dockerfile` ni en otro sitio.
"""

SPACY_MODEL = "es_core_news_sm"
MEDDOCAN_MODEL = "BSC-NLP4BIA/bsc-bio-ehr-es-meddocan"
