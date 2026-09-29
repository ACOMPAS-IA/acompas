import pytest

from app.services.anonymization import AnonymizationService


def test_anonymization_service_returns_result():
    service = AnonymizationService()

    result = service.anonymize("Texto de prueba")

    assert result.anonymized_text == "Texto de prueba"
    assert result.entities_count == {}


def test_anonymization_service_rejects_empty_text():
    service = AnonymizationService()

    with pytest.raises(ValueError):
        service.anonymize("")
