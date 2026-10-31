"""Avisos del analizador sin texto del documento (#48, R-04/T-04)."""

import logging
import warnings
from contextlib import contextmanager
from pathlib import Path

import pytest
from presidio_analyzer.nlp_engine import TransformersNlpEngine

from app.services.anonymization.analyzer import (
    DEFAULT_ENTITIES,
    DISCARD_REASON_ALIGNMENT,
    DISCARD_REASON_PROCESSING,
    SanitizedTransformersNlpEngine,
    _sanitize_analysis_warnings,
    build_analyzer,
)

MARKER = "MARCADOR_SECRETO_XYZ"
DOCUMENT = (
    f"Paciente {MARKER}. DNI 12345678Z. "
    "Fecha: 15/09/2026. Teléfono: 612345678."
)

ALIGNMENT_WARNING = (
    f"Skipping annotation, {{'word': '{MARKER}'}} is overlapping or can't be "
    f"aligned for doc '{DOCUMENT}'"
)
PROCESSING_WARNING = f"Unable to process, skipping annotation for doc '{DOCUMENT}'"


@contextmanager
def _default_warning_state():
    """Aísla el estado de warnings del que impone pytest a cada test."""
    with warnings.catch_warnings():
        warnings.resetwarnings()
        yield


@contextmanager
def _recording_showwarning():
    """Sustituye showwarning por un registrador de avisos reenviados."""
    forwarded = []

    def record(message, category, filename, lineno, file=None, line=None):
        forwarded.append(
            {
                "message": message,
                "category": category,
                "filename": filename,
                "lineno": lineno,
                "file": file,
                "line": line,
            }
        )

    original = warnings.showwarning
    warnings.showwarning = record
    try:
        yield forwarded
    finally:
        warnings.showwarning = original


def _emit_alignment_warning() -> None:
    """Ambos avisos se emiten desde la misma ubicación, como en el pipeline."""
    warnings.warn(ALIGNMENT_WARNING, UserWarning)


def test_repeated_known_warnings_are_all_counted():
    with _default_warning_state():
        with _recording_showwarning() as forwarded:
            with _sanitize_analysis_warnings() as discarded:
                _emit_alignment_warning()
                _emit_alignment_warning()

    # Con action="default"/"once", Python suprimiría el segundo aviso antes de
    # llegar a showwarning y el contador mediría de menos.
    assert discarded[DISCARD_REASON_ALIGNMENT] == 2
    assert forwarded == []


def test_known_warnings_are_summarized_without_document_text(caplog):
    caplog.set_level(logging.DEBUG)

    with _default_warning_state():
        with _recording_showwarning() as forwarded:
            with _sanitize_analysis_warnings() as discarded:
                _emit_alignment_warning()
                warnings.warn(PROCESSING_WARNING, UserWarning)

    assert forwarded == []
    assert discarded[DISCARD_REASON_ALIGNMENT] == 1
    assert discarded[DISCARD_REASON_PROCESSING] == 1

    logged = "\n".join(record.getMessage() for record in caplog.records)

    assert "1 aviso(s) descartado(s) por solapamiento o alineación" in logged
    assert "1 aviso(s) descartado(s) por fallo al procesar el texto" in logged
    assert MARKER not in logged
    assert DOCUMENT not in logged


def test_unrelated_warning_is_forwarded_unchanged():
    with _default_warning_state():
        with _recording_showwarning() as forwarded:
            with _sanitize_analysis_warnings() as discarded:
                warnings.warn("Aviso ajeno de prueba", UserWarning)

    assert discarded == {}
    assert len(forwarded) == 1

    forwarded_warning = forwarded[0]

    assert str(forwarded_warning["message"]) == "Aviso ajeno de prueba"
    assert forwarded_warning["category"] is UserWarning
    assert Path(forwarded_warning["filename"]).name == Path(__file__).name
    assert forwarded_warning["lineno"] > 0
    assert forwarded_warning["file"] is None
    assert forwarded_warning["line"] is None


def test_known_prefix_with_another_category_is_forwarded():
    with _default_warning_state():
        with _recording_showwarning() as forwarded:
            with _sanitize_analysis_warnings() as discarded:
                warnings.warn(ALIGNMENT_WARNING, RuntimeWarning)

    assert discarded == {}
    assert len(forwarded) == 1
    assert forwarded[0]["category"] is RuntimeWarning


def test_showwarning_is_restored_when_sanitizer_fails():
    original = warnings.showwarning

    with pytest.raises(RuntimeError):
        with _sanitize_analysis_warnings():
            raise RuntimeError("fallo simulado")

    assert warnings.showwarning is original


def test_process_text_restores_showwarning_when_it_fails(monkeypatch):
    def fail(self, text, language):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr(TransformersNlpEngine, "process_text", fail)
    engine = object.__new__(SanitizedTransformersNlpEngine)
    original = warnings.showwarning

    with pytest.raises(RuntimeError, match="fallo simulado"):
        engine.process_text("texto sintético", "es")

    assert warnings.showwarning is original


@pytest.fixture(scope="module")
def analyzer():
    return build_analyzer()


def test_build_analyzer_uses_sanitized_engine(analyzer):
    assert isinstance(analyzer.nlp_engine, SanitizedTransformersNlpEngine)
    assert analyzer.log_decision_process is False
    assert logging.getLogger("presidio-analyzer").level == logging.INFO


def test_analysis_does_not_leak_document_text(analyzer, caplog, capsys):
    caplog.set_level(logging.DEBUG)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        results = analyzer.analyze(
            text=DOCUMENT,
            language="es",
            entities=DEFAULT_ENTITIES,
        )

    captured = capsys.readouterr()
    warnings_text = "\n".join(str(warning.message) for warning in caught)
    logged_text = "\n".join(record.getMessage() for record in caplog.records)
    output_text = captured.out + captured.err

    assert results
    assert "aviso(s) descartado(s)" in logged_text

    for leaked in (warnings_text, logged_text, output_text):
        assert MARKER not in leaked
        assert DOCUMENT not in leaked
