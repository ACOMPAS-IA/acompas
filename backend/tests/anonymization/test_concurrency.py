"""Cerrojos de la construcción perezosa del analyzer (#119).

Sin ellos, dos peticiones simultáneas construyen el modelo dos veces: son dos
analyzers en memoria y minutos de carga. Los hilos se sincronizan con una
barrera para que la carrera sea determinista, y el constructor falso duerme
para ensanchar la ventana.
"""

import threading
import time

from app.api import anonymization as api
from app.services.anonymization import service as service_module

THREADS = 8
DELAY_SECONDS = 0.05


class SlowAnalyzerBuilder:
    """Sustituye a build_analyzer y cuenta cuántas veces se construye."""

    def __init__(self):
        self.calls = 0
        self.sentinel = object()
        self._lock = threading.Lock()

    def __call__(self):
        with self._lock:
            self.calls += 1
        time.sleep(DELAY_SECONDS)
        return self.sentinel


def run_concurrently(access):
    """Lanza THREADS hilos que llaman a access() a la vez y devuelve el resultado."""
    barrier = threading.Barrier(THREADS)
    results = []

    def target():
        barrier.wait()
        results.append(access())

    threads = [threading.Thread(target=target) for _ in range(THREADS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return results


def test_analyzer_is_built_once_under_concurrency(monkeypatch):
    builder = SlowAnalyzerBuilder()
    monkeypatch.setattr(service_module, "build_analyzer", builder)

    service = service_module.AnonymizationService()
    results = run_concurrently(lambda: service.analyzer)

    assert builder.calls == 1
    assert len(results) == THREADS
    assert all(result is builder.sentinel for result in results)


def test_default_service_is_created_once_under_concurrency(monkeypatch):
    created = []

    class CountingService:
        def __init__(self):
            created.append(self)
            time.sleep(DELAY_SECONDS)

    monkeypatch.setattr(api, "AnonymizationService", CountingService)
    monkeypatch.setattr(api, "_service", None)

    results = run_concurrently(api.get_anonymization_service)

    assert len(created) == 1
    assert len(results) == THREADS
    assert all(result is created[0] for result in results)
