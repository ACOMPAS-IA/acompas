from pydantic import BaseModel, ConfigDict


class PromptTemplate(BaseModel):
    """Texto de un prompt con su versión y su huella SHA-256."""

    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    text: str
    sha256: str
