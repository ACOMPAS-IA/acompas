"""Endpoint HTTP de anonimización (ACO-024).

Expone el servicio de ACO-023 sin cambiar su contrato. Ninguna respuesta
devuelve el texto original, tampoco los errores de validación. Un fallo
inesperado se sanea antes de relanzarlo, para que el servidor no registre el
texto en la traza (ACO-025, P7).
"""

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.auth import get_current_user
from app.services.anonymization import AnonymizationService
from app.services.anonymization.config import AnonymizationConfigurationError
from app.services.anonymization.models import AnonymizationRequest, AnonymizationResult

ANONYMIZATION_PATH = "/api/anonymization"
INTERNAL_ERROR = "anonymization_failed"

logger = logging.getLogger("app.api.anonymization")

router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])


@lru_cache(maxsize=1)
def _default_service() -> AnonymizationService:
    # El analyzer se construye de forma perezosa y se reutiliza entre
    # peticiones: cargar el modelo en cada llamada sería inviable.
    return AnonymizationService()


def get_anonymization_service() -> AnonymizationService:
    """Dependencia sustituible en los tests por un servicio sin modelo."""
    return _default_service()


async def anonymization_validation_handler(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    """Sanea los errores de validación de esta ruta (ficha ACO-024, P5).

    FastAPI incluye el valor recibido en cada error de validación. Devolverlo
    incumpliría la prohibición de devolver el texto original. Para el resto de
    rutas se mantiene el handler por defecto.
    """
    if request.url.path != ANONYMIZATION_PATH:
        return await request_validation_exception_handler(request, error)

    error_types = {item["type"] for item in error.errors()}
    detail = "text_too_long" if "string_too_long" in error_types else "invalid_request"
    return JSONResponse(status_code=422, content={"detail": detail})


@router.post("/anonymization", response_model=AnonymizationResult)
def anonymize(
    payload: AnonymizationRequest,
    service: Annotated[AnonymizationService, Depends(get_anonymization_service)],
) -> AnonymizationResult:
    """Anonimiza un texto clínico y devuelve el resultado o el motivo.

    Los estados `validado`, `retenido` e `ilegible` devuelven 200. En ningún
    caso se devuelve el texto original.
    """
    try:
        return service.anonymize(payload.text)
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
