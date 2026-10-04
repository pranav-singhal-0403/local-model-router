from fastapi import APIRouter

from backend.ollama_client import OllamaClient
from backend.qdrant_client import QdrantVectorStore


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check():

    ollama = OllamaClient()
    qdrant = QdrantVectorStore()

    ollama_status = await ollama.health_check()

    try:
        qdrant_status = qdrant.collection_exists()
    except Exception:
        qdrant_status = False

    return {
        "status": "ok",
        "services": {
            "ollama": ollama_status,
            "qdrant": qdrant_status,
        },
    }