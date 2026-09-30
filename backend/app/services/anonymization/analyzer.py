"""Construcción del AnalyzerEngine de Presidio para español con MEDDOCAN."""

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import TransformersNlpEngine, NerModelConfiguration

MEDDOCAN_MODEL = "BSC-NLP4BIA/bsc-bio-ehr-es-meddocan"

MEDDOCAN_ENTITY_MAPPING = {
    "NOMBRE_SUJETO_ASISTENCIA": "PERSON",
    "NOMBRE_PERSONAL_SANITARIO": "PERSON",
    "OTROS_SUJETO_ASISTENCIA": "PERSON",
    "FAMILIARES_SUJETO_ASISTENCIA": "PERSON",
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

DEFAULT_ENTITIES = [
    "PERSON",
    "DATE_TIME",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "ES_DNI",
    "ES_HISTORIA_CLINICA",
    "ID_ASEGURAMIENTO",
    "ID_CONTACTO_ASISTENCIAL",
    "ID_EMPLEO_PERSONAL_SANITARIO",
    "ID_TITULACION_PERSONAL_SANITARIO",
    "CALLE",
]

MIN_SCORE_THRESHOLD = 0.35


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

    nlp_engine = TransformersNlpEngine(
        models=model_config,
        ner_model_configuration=ner_model_configuration,
    )

    return AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["es"],
    )
