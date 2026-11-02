"""Tests del servicio de anonimización (ACO-023, AC-13 a AC-16)."""

from types import SimpleNamespace

import pytest

from app.services.anonymization import AnonymizationService
from app.services.anonymization import confidence as confidence_module
from app.services.anonymization.analyzer import build_analyzer
from app.services.anonymization.config import load_settings
from app.services.anonymization.models import (
    REASON_EMPTY_TEXT,
    REASON_LOW_CONFIDENCE,
    AnonymizationStatus,
)
from tests.synthetic_data import load_document


class FakeAnalyzer:
    def __init__(self, results=()):
        self.results = list(results)
        self.calls = 0

    def analyze(self, text, language, entities):
        self.calls += 1
        return self.results


def result(entity_type, text, fragment, score=0.99, occurrence=0):
    start = -1
    for _ in range(occurrence + 1):
        start = text.index(fragment, start + 1)
    return SimpleNamespace(
        entity_type=entity_type,
        start=start,
        end=start + len(fragment),
        score=score,
    )


def service_with(text, results, settings=None):
    analyzer = FakeAnalyzer([result(*item) for item in results])
    loader = (lambda: settings) if settings is not None else load_settings
    return AnonymizationService(analyzer=analyzer, settings_loader=loader), analyzer


@pytest.mark.parametrize("text", ["", "   ", "\n\t "])
def test_empty_text_is_illegible_without_calling_the_model(text):
    analyzer = FakeAnalyzer()
    service = AnonymizationService(analyzer=analyzer, settings_loader=load_settings)

    output = service.anonymize(text)

    assert output.status == AnonymizationStatus.ILEGIBLE
    assert output.confidence is None
    assert output.anonymized_text is None
    assert output.entities_count == {}
    assert output.reason == REASON_EMPTY_TEXT
    assert analyzer.calls == 0


def test_validated_document_returns_anonymized_text_and_contract():
    text = "DNI: 12345678Z."
    service, analyzer = service_with(text, [("ES_DNI", text, "12345678Z", 1.0)])

    output = service.anonymize(text)

    assert analyzer.calls == 1
    assert output.status == AnonymizationStatus.VALIDADO
    assert output.confidence == 1.0
    assert output.anonymized_text == "DNI: [DNI]."
    assert output.entities_count == {"ES_DNI": 1}
    assert output.reason is None


def test_low_confidence_document_is_retained_without_text():
    settings = load_settings()
    score = (settings.finding_threshold + settings.document_threshold) / 2
    text = "DNI: 12345678Z."
    service, _ = service_with(
        text, [("ES_DNI", text, "12345678Z", score)], settings=settings
    )

    output = service.anonymize(text)

    assert output.status == AnonymizationStatus.RETENIDO
    assert output.confidence == score
    assert output.anonymized_text is None
    assert output.entities_count == {}
    assert output.reason == REASON_LOW_CONFIDENCE
    assert "12345678Z" not in str(output.model_dump())


def test_context_types_do_not_change_the_text_or_the_confidence():
    text = "Edad: 68 años. Sexo: Mujer."
    service, _ = service_with(
        text,
        [
            ("AGE", text, "68 años"),
            ("SEXO", text, "Mujer"),
        ],
    )

    output = service.anonymize(text)

    assert output.status == AnonymizationStatus.VALIDADO
    assert output.confidence == 1.0
    assert output.anonymized_text == text
    assert output.entities_count == {}


def test_birth_date_is_replaced_and_clinical_dates_are_kept():
    text = (
        "Fecha de nacimiento: 14/03/1958. "
        "Fecha del informe: 12/09/2026."
    )
    service, _ = service_with(
        text,
        [
            ("DATE_TIME", text, "14/03/1958"),
            ("DATE_TIME", text, "12/09/2026"),
        ],
    )

    output = service.anonymize(text)

    assert output.status == AnonymizationStatus.VALIDADO
    assert output.anonymized_text == (
        "Fecha de nacimiento: [FECHA_NACIMIENTO]. "
        "Fecha del informe: 12/09/2026."
    )
    assert output.entities_count == {"DATE_TIME": 1}


def test_people_are_labelled_and_numbered(monkeypatch):
    text = "Dra. Inés Carrascal Ochoa. Paciente: Rosario Albendea Quintanar."
    service, _ = service_with(
        text,
        [
            ("PERSONAL_SANITARIO", text, "Inés Carrascal Ochoa"),
            ("PACIENTE", text, "Rosario Albendea Quintanar"),
        ],
    )
    monkeypatch.setattr(
        confidence_module,
        "_token_person_probabilities",
        lambda text, analyzer: [(0, len(text), 0.99)],
    )

    output = service.anonymize(text)

    assert output.status == AnonymizationStatus.VALIDADO
    assert output.anonymized_text == (
        "Dra. [SANITARIO_1]. Paciente: [PACIENTE]."
    )
    assert "Inés Carrascal Ochoa" not in output.anonymized_text
    assert "Rosario Albendea Quintanar" not in output.anonymized_text


def test_findings_below_the_finding_threshold_do_not_affect_confidence():
    settings = load_settings()
    text = "DNI: 12345678Z. Teléfono: 600 123 456."
    service, _ = service_with(
        text,
        [
            ("ES_DNI", text, "12345678Z", 1.0),
            (
                "PHONE_NUMBER",
                text,
                "600 123 456",
                max(0.0, settings.finding_threshold - 0.01),
            ),
        ],
        settings=settings,
    )

    output = service.anonymize(text)

    assert output.status == AnonymizationStatus.VALIDADO
    assert output.confidence == 1.0
    assert output.entities_count == {"ES_DNI": 1}


def test_service_does_not_persist_the_original_on_retention():
    settings = load_settings()
    score = (settings.finding_threshold + settings.document_threshold) / 2
    text = "Paciente: Rosario Albendea Quintanar."
    service, _ = service_with(
        text, [("ES_DNI", text, "Rosario Albendea Quintanar", score)], settings=settings
    )

    output = service.anonymize(text)

    assert output.status == AnonymizationStatus.RETENIDO
    assert output.anonymized_text is None
    assert "Rosario Albendea Quintanar" not in str(output.model_dump())


@pytest.fixture(scope="module")
def model_service():
    return AnonymizationService(analyzer=build_analyzer())


@pytest.mark.parametrize(
    "name",
    [
        "informe_patologia_01.txt",
        "analitica_01.txt",
        "carta_oncologia_01.txt",
    ],
)
def test_synthetic_corpus_is_validated_with_the_initial_configuration(model_service, name):
    settings = load_settings()
    text = load_document(name)

    output = model_service.anonymize(text)

    assert output.status == AnonymizationStatus.VALIDADO
    assert output.confidence is not None
    assert output.confidence >= settings.document_threshold
    assert output.anonymized_text is not None
    assert "12345678Z" not in output.anonymized_text
    assert "Rosario Albendea Quintanar" not in output.anonymized_text
    assert "ALBENDEA QUINTANAR" not in output.anonymized_text
