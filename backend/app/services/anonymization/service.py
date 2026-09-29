from .models import AnonymizationResult


class AnonymizationService:
    """Servicio de anonimización de ACOMPAS.

    El motor de detección y anonimización se incorporará
    progresivamente en ACO-021, ACO-022 y ACO-023.
    """

    def anonymize(self, text: str) -> AnonymizationResult:
        if not text:
            raise ValueError("text must not be empty")

        # ACO-020: contrato del servicio.
        # La implementación real se incorporará en ACO-021/022/023.
        return AnonymizationResult(
            anonymized_text=text,
            entities_count={},
        )
