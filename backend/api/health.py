from fastapi import APIRouter, Request

from backend.config import EMBEDDING_CONFIG


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check(request: Request):

    state = request.app.state.rag

    try:
        ollama_status = await state.ollama.health_check()
    except Exception:
        ollama_status = False

    try:
        qdrant_status = state.qdrant.collection_exists()
    except Exception:
        qdrant_status = False

    return {
        "status": "ok",
        "services": {
            "ollama": ollama_status,
            "qdrant": qdrant_status,
        },
        "models": {
            "llm": state.ollama.model,
            "embedding": EMBEDDING_CONFIG.get("model"),
            "embedding_dimension": state.embedder.dimension,
        },
    }