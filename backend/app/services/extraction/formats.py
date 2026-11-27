"""Detección del formato de un documento por su firma (ACO-035).

La extensión y el tipo declarado por el cliente no se usan: un `.txt`
renombrado no es un PDF. Es lo que fija la ficha, sección 8.1.
"""

from enum import Enum

from .models import UnsupportedFormatError


class DocumentFormat(str, Enum):
    PDF = "pdf"
    JPEG = "jpeg"
    PNG = "png"


# Firmas al principio del contenido. El JPEG admite variantes, pero todas
# empiezan por los mismos tres bytes.
SIGNATURES = (
    (b"%PDF-", DocumentFormat.PDF),
    (b"\xff\xd8\xff", DocumentFormat.JPEG),
    (b"\x89PNG\r\n\x1a\n", DocumentFormat.PNG),
)


def detect_format(data: bytes) -> DocumentFormat:
    """Devuelve el formato del documento o lanza `UnsupportedFormatError`."""
    for signature, document_format in SIGNATURES:
        if data.startswith(signature):
            return document_format
    raise UnsupportedFormatError("firma no admitida")
