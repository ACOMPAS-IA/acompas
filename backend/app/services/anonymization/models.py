from pydantic import BaseModel, Field


class AnonymizationRequest(BaseModel):
    text: str = Field(min_length=1)


class AnonymizationResult(BaseModel):
    anonymized_text: str
    entities_count: dict[str, int] = Field(default_factory=dict)
