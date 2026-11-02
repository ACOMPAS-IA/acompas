from .analyzer import build_analyzer
from .confidence import document_confidence
from .config import load_settings
from .detection import detect_entities
from .models import (
    REASON_EMPTY_TEXT,
    REASON_LOW_CONFIDENCE,
    AnonymizationResult,
    AnonymizationStatus,
)
from .policy import select_findings
from .replacement import assign_labels, count_entities, substitute


class AnonymizationService:
    """Servicio de anonimización de ACOMPAS.

    Aplica la detección de ACO-022, la política y los umbrales de ACO-023, y
    devuelve el texto anonimizado o el motivo por el que el documento no pasa.
    No persiste el original ni el resultado retenido y no registra contenido.
    """

    def __init__(self, analyzer=None, settings_loader=load_settings):
        self._analyzer = analyzer
        self._settings_loader = settings_loader

    @property
    def analyzer(self):
        if self._analyzer is None:
            self._analyzer = build_analyzer()
        return self._analyzer

    def anonymize(self, text: str) -> AnonymizationResult:
        if not text or not text.strip():
            return AnonymizationResult(
                status=AnonymizationStatus.ILEGIBLE,
                confidence=None,
                anonymized_text=None,
                entities_count={},
                reason=REASON_EMPTY_TEXT,
            )

        settings = self._settings_loader()
        detections = detect_entities(text, self.analyzer)
        findings = select_findings(text, detections, settings)
        confidence = document_confidence(text, findings, self.analyzer)

        if confidence < settings.document_threshold:
            return AnonymizationResult(
                status=AnonymizationStatus.RETENIDO,
                confidence=confidence,
                anonymized_text=None,
                entities_count={},
                reason=REASON_LOW_CONFIDENCE,
            )

        labels = assign_labels(text, findings)
        return AnonymizationResult(
            status=AnonymizationStatus.VALIDADO,
            confidence=confidence,
            anonymized_text=substitute(text, findings, labels),
            entities_count=count_entities(findings),
        )
