from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.anonymization import (
    anonymization_validation_handler,
    router as anonymization_router,
)
from app.api.conversation import router as conversation_router
from app.logging import configure_logging

# Se configura al importar/arrancar, nunca en cada petición (ADR-015 §4).
configure_logging()

app = FastAPI(
    title="ACOMPAS API",
    version="0.1.0",
)

app.include_router(anonymization_router)
app.include_router(conversation_router)
app.add_exception_handler(RequestValidationError, anonymization_validation_handler)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
