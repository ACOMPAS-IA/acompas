from fastapi import FastAPI

from app.api.conversation import router as conversation_router

app = FastAPI(
    title="ACOMPAS API",
    version="0.1.0",
)

app.include_router(conversation_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
