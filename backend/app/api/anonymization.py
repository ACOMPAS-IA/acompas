"""Endpoints HTTP de anonimización (ACO-024 y ACO-035).

Expone el servicio de ACO-023 sin cambiar su contrato y añade la ruta que
recibe un fichero y le extrae el texto. Ninguna respuesta devuelve el texto
original, tampoco los errores de validación. Un fallo inesperado se sanea
antes de relanzarlo, para que el servidor no registre el texto en la traza
(ACO-025, P7).
"""

import logging
import threading
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.auth import get_current_user
from app.services.anonymization import AnonymizationService
from app.services.anonymization.config import AnonymizationConfigurationError
from app.services.anonymization.models import (
    AnonymizationRequest,
    AnonymizationResult,
    AnonymizationStatus,
)
from app.services.extraction import (
    DocumentExtractor,
    ExtractionConfigurationError,
    FileTooLargeError,
    TextTooLongError,
    UnsupportedFormatError,
)
from app.services.extraction.service import MAX_UPLOAD_BYTES

ANONYMIZATION_PATH = "/api/anonymization"
FILE_PATH = "/api/anonymization/file"
INTERNAL_ERROR = "anonymization_failed"

# Rutas cuyo error de validación se sanea: FastAPI incluiría el valor recibido.
SANITIZED_PATHS = frozenset({ANONYMIZATION_PATH, FILE_PATH})

logger = logging.getLogger("app.api.anonymization")

router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])


# El analyzer se construye de forma perezosa y se reutiliza entre peticiones:
# cargar el modelo en cada llamada sería inviable. `lru_cache` no garantiza una
# sola ejecución si dos hilos fallan el caché a la vez, y dos servicios son dos
# analyzers; el cerrojo lo evita (#119).
_service_lock = threading.Lock()
_service: AnonymizationService | None = None


def get_anonymization_service() -> AnonymizationService:
    """Dependencia sustituible en los tests por un servicio sin modelo."""
    global _service
    if _service is None:
        with _service_lock:
            if _service is None:
                _service = AnonymizationService()
    return _service


# Aquí `lru_cache` basta: construir el extractor no descarga modelos y dos
# instancias no cuestan memoria, al contrario que el analyzer (#119).
@lru_cache(maxsize=1)
def _default_extractor() -> DocumentExtractor:
    return DocumentExtractor()


def get_document_extractor() -> DocumentExtractor:
    """Dependencia sustituible en los tests por un extractor sin OCR."""
    return _default_extractor()


async def anonymization_validation_handler(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    """Sanea los errores de validación de estas rutas (ACO-024, P5).

    FastAPI incluye el valor recibido en cada error de validación. Devolverlo
    incumpliría la prohibición de devolver el texto original. Para el resto de
    rutas se mantiene el handler por defecto.
    """
    if request.url.path not in SANITIZED_PATHS:
        return await request_validation_exception_handler(request, error)

    if request.url.path == FILE_PATH:
        return JSONResponse(status_code=422, content={"detail": "invalid_request"})

    error_types = {item["type"] for item in error.errors()}
    detail = "text_too_long" if "string_too_long" in error_types else "invalid_request"
    return JSONResponse(status_code=422, content={"detail": detail})


def _anonymize(service: AnonymizationService, text: str) -> AnonymizationResult:
    try:
        return service.anonymize(text)
    except AnonymizationConfigurationError:
        # El mensaje de la configuración no se propaga.
        raise HTTPException(
            status_code=503, detail="anonymization_not_configured"
        ) from None
    except Exception as error:
        # El servidor registra la traza de la excepción que sale del endpoint.
        # Se relanza una excepción sin mensaje ni cadena para que no pueda
        # incluir el texto del documento (ACO-025, P7).
        logger.error("Anonymization failed: %s", type(error).__name__)
        raise RuntimeError(INTERNAL_ERROR) from None


def _read_upload(file: UploadFile) -> bytes:
    """Lee el fichero y cierra su temporal pase lo que pase.

    El criterio de la ficha es que no quede residuo del original, no que no
    haya escritura: Starlette escribe en un temporal lo que pasa de 1 MB y
    cerrar el fichero lo borra.
    """
    try:
        return file.file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        file.file.close()


@router.post("/anonymization", response_model=AnonymizationResult)
def anonymize(
    payload: AnonymizationRequest,
    service: Annotated[AnonymizationService, Depends(get_anonymization_service)],
) -> AnonymizationResult:
    """Anonimiza un texto clínico y devuelve el resultado o el motivo.

    Los estados `validado`, `retenido` e `ilegible` devuelven 200. En ningún
    caso se devuelve el texto original.
    """
    return _anonymize(service, payload.text)


@router.post("/anonymization/file", response_model=AnonymizationResult)
def anonymize_file(
    file: Annotated[UploadFile, File()],
    service: Annotated[AnonymizationService, Depends(get_anonymization_service)],
    extractor: Annotated[DocumentExtractor, Depends(get_document_extractor)],
) -> AnonymizationResult:
    """Extrae el texto de un PDF, JPG o PNG y lo anonimiza (ACO-035).

    El fichero se lee en memoria y su temporal se cierra antes de responder.
    El nombre del fichero no se usa ni se registra. Los estados y el resultado
    son los mismos que los del endpoint de texto.
    """
    data = _read_upload(file)

    try:
        extracted = extractor.extract(data)
    except FileTooLargeError:
        raise HTTPException(status_code=413, detail="file_too_large") from None
    except UnsupportedFormatError:
        raise HTTPException(status_code=415, detail="unsupported_format") from None
    except TextTooLongError:
        raise HTTPException(status_code=422, detail="text_too_long") from None
    except ExtractionConfigurationError:
        raise HTTPException(
            status_code=503, detail="extraction_not_configured"
        ) from None
    except Exception as error:
        logger.error("Extraction failed: %s", type(error).__name__)
        raise RuntimeError(INTERNAL_ERROR) from None

    if extracted.reason is not None:
        # Ilegible: no se llega a la anonimización ni se devuelve el texto.
        return AnonymizationResult(
            status=AnonymizationStatus.ILEGIBLE, reason=extracted.reason
        )

    return _anonymize(service, extracted.text)
