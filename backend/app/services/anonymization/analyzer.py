"""Construcción del AnalyzerEngine de Presidio para español con MEDDOCAN."""

import logging
import re
import threading
import warnings
from collections import Counter
from contextlib import contextmanager
from typing import Iterator

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import (
    NerModelConfiguration,
    NlpArtifacts,
    TransformersNlpEngine,
)

from .recognizers import build_recognizers

logger = logging.getLogger("app.services.anonymization")

# Presidio registra en DEBUG los lemas del contexto del documento
# («Context list is: ...»). INFO conserva avisos y errores útiles y corta esa
# fuga de contenido (R-04, T-04).
logging.getLogger("presidio-analyzer").setLevel(logging.INFO)

# Motivos normalizados de los avisos del pipeline NLP que incluyen texto del
# documento. El resumen nunca usa el mensaje original (R-04).
DISCARD_REASON_ALIGNMENT = "solapamiento o alineación"
DISCARD_REASON_PROCESSING = "fallo al procesar el texto"

# Prefijos de spacy_huggingface_pipelines en las versiones auditadas de la
# imagen. Se clasifican en memoria, pero ni el fragmento ni el documento llegan
# a los registros.
_KNOWN_WARNING_REASONS = {
    "Skipping annotation, ": DISCARD_REASON_ALIGNMENT,
    "Unable to process, skipping annotation for doc ": DISCARD_REASON_PROCESSING,
}

# warnings.showwarning es estado global del proceso: el lock serializa las
# llamadas propias al motor mientras dura la sustitución.
_ANALYSIS_LOCK = threading.Lock()


@contextmanager
def _sanitize_analysis_warnings() -> Iterator[Counter[str]]:
    """Sustituye showwarning para descontar los avisos que incluyen texto.

    Instala dos filtros globales temporales, exactos y restaurados al salir,
    con action="always" para que Python no suprima repeticiones antes de
    contarlas. Los avisos no reconocidos se reenvían al manejador original con
    los mismos argumentos.
    """
    discarded: Counter[str] = Counter()
    original_showwarning = warnings.showwarning

    def sanitized_showwarning(message, category, filename, lineno, file=None, line=None):
        if issubclass(category, UserWarning):
            for prefix, reason in _KNOWN_WARNING_REASONS.items():
                if str(message).startswith(prefix):
                    discarded[reason] += 1
                    return
        original_showwarning(message, category, filename, lineno, file, line)

    with warnings.catch_warnings():
        for prefix in _KNOWN_WARNING_REASONS:
            warnings.filterwarnings(
                action="always",
                message=rf"^{re.escape(prefix)}",
                category=UserWarning,
            )
        warnings.showwarning = sanitized_showwarning
        try:
            yield discarded
        finally:
            warnings.showwarning = original_showwarning

    if discarded:
        logger.warning(
            "Anonimización: %s",
            ", ".join(
                f"{discarded[reason]} aviso(s) descartado(s) por {reason}"
                for reason in (DISCARD_REASON_ALIGNMENT, DISCARD_REASON_PROCESSING)
                if discarded[reason]
            ),
        )


class SanitizedTransformersNlpEngine(TransformersNlpEngine):
    """Motor NLP que evita que los avisos del pipeline filtren texto (R-04)."""

    def process_text(self, text: str, language: str) -> NlpArtifacts:
        # El lock cubre únicamente process_text. No impide que otro código del
        # proceso manipule warnings durante la ventana: es una mitigación
        # proporcionada, no una garantía process-wide.
        with _ANALYSIS_LOCK:
            with _sanitize_analysis_warnings():
                return super().process_text(text, language)

MEDDOCAN_MODEL = "BSC-NLP4BIA/bsc-bio-ehr-es-meddocan"

MEDDOCAN_ENTITY_MAPPING = {
    # Personas con rol; PERSON es el tipo genérico cuando el rol no está claro
    # (ficha ACO-022, P4).
    "NOMBRE_SUJETO_ASISTENCIA": "PACIENTE",
    "NOMBRE_PERSONAL_SANITARIO": "PERSONAL_SANITARIO",
    "OTROS_SUJETO_ASISTENCIA": "PERSON",
    "FAMILIARES_SUJETO_ASISTENCIA": "FAMILIAR",
    "ID_SUJETO_ASISTENCIA": "ES_HISTORIA_CLINICA",
    "ID_ASEGURAMIENTO": "ID_ASEGURAMIENTO",
    "ID_CONTACTO_ASISTENCIAL": "ID_CONTACTO_ASISTENCIAL",
    "ID_EMPLEO_PERSONAL_SANITARIO": "ID_EMPLEO_PERSONAL_SANITARIO",
    "ID_TITULACION_PERSONAL_SANITARIO": "ID_TITULACION_PERSONAL_SANITARIO",
    "CORREO_ELECTRONICO": "EMAIL_ADDRESS",
    "NUMERO_TELEFONO": "PHONE_NUMBER",
    "NUMERO_FAX": "PHONE_NUMBER",
    "FECHAS": "DATE_TIME",
    "CALLE": "CALLE",
    "HOSPITAL": "HOSPITAL",
    "INSTITUCION": "INSTITUCION",
    "CENTRO_SALUD": "CENTRO_SALUD",
    "TERRITORIO": "TERRITORIO",
    "PAIS": "PAIS",
    "PROFESION": "PROFESION",
    "EDAD_SUJETO_ASISTENCIA": "AGE",
    "SEXO_SUJETO_ASISTENCIA": "SEXO",
}

# Todo lo que detecta el motor, se anonimice o no. Qué se anonimiza y con qué
# umbral lo decide ACO-023 (ficha ACO-022, P9).
DEFAULT_ENTITIES = sorted(
    set(MEDDOCAN_ENTITY_MAPPING.values())
    | {entity for recognizer in build_recognizers() for entity in recognizer.supported_entities}
)

# Reconocedores predefinidos de Presidio sustituidos por los propios (ficha ACO-022, P5).
REPLACED_PREDEFINED_RECOGNIZERS = ["EsNifRecognizer", "EsNieRecognizer"]


def get_token_pipeline(analyzer: AnalyzerEngine):
    """Devuelve el pipeline de token classification ya cargado.

    Es un accesor de lectura: no cambia el modelo ni la configuración del motor.
    ACO-023 lo usa para obtener las probabilidades de todas las etiquetas de
    persona, que Presidio no expone en su resultado agregado. Según la versión,
    el componente es el `HFTokenPipe` de spacy_huggingface_pipelines (atributo
    `hf_pipeline`) o el `HuggingFaceTokenPipe` integrado en Presidio (atributo
    `pipeline`), y su nombre también cambia (`hf_token_pipe` o
    `presidio_hf_token_pipe`). Se localiza por el atributo, no por el nombre.
    """
    nlp = analyzer.nlp_engine.nlp["es"]
    for _, component in nlp.pipeline:
        pipeline = getattr(component, "hf_pipeline", None)
        if pipeline is None:
            candidate = getattr(component, "pipeline", None)
            if candidate is not None and hasattr(candidate, "tokenizer"):
                pipeline = candidate
        if pipeline is not None:
            return pipeline
    raise RuntimeError(
        "El motor NLP no expone el pipeline de token classification"
    )


def build_analyzer() -> AnalyzerEngine:
    """Construye un AnalyzerEngine configurado con MEDDOCAN."""
    model_config = [
        {
            "lang_code": "es",
            "model_name": {
                "spacy": "es_core_news_sm",
                "transformers": MEDDOCAN_MODEL,
            },
        }
    ]

    ner_model_configuration = NerModelConfiguration(
        model_to_presidio_entity_mapping=MEDDOCAN_ENTITY_MAPPING,
        alignment_mode="expand",
        aggregation_strategy="simple",
        labels_to_ignore=["O"],
    )

    nlp_engine = SanitizedTransformersNlpEngine(
        models=model_config,
        ner_model_configuration=ner_model_configuration,
    )

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["es"],
        # Explícito por privacidad: el trazado de decisiones puede incluir
        # contenido del documento (R-04).
        log_decision_process=False,
    )

    for name in REPLACED_PREDEFINED_RECOGNIZERS:
        analyzer.registry.remove_recognizer(name, language="es")
    for recognizer in build_recognizers():
        analyzer.registry.add_recognizer(recognizer)

    return analyzer
