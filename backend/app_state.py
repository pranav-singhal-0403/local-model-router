from dataclasses import dataclass

from backend.answer_generator import AnswerGenerator
from backend.embeddings_dense import DenseEmbedder
from backend.ingestion_pipeline import IngestionPipeline
from backend.ollama_client import OllamaClient
from backend.qdrant_client import QdrantVectorStore
from backend.retreiver_dense import DenseRetriever


@dataclass
class AppState:
    embedder: DenseEmbedder
    qdrant: QdrantVectorStore
    retriever: DenseRetriever
    ollama: OllamaClient
    generator: AnswerGenerator
    ingestion: IngestionPipeline


def create_app_state() -> AppState:
    embedder = DenseEmbedder()

    qdrant = QdrantVectorStore()

    qdrant.create_collection(
        vector_size=embedder.dimension
    )

    retriever = DenseRetriever(
        embedder=embedder,
        vector_store=qdrant,
    )

    ollama = OllamaClient()

    generator = AnswerGenerator(
        ollama_client=ollama,
    )

    ingestion = IngestionPipeline(
        embedder=embedder,
        vector_store=qdrant,
    )

    return AppState(
        embedder=embedder,
        qdrant=qdrant,
        retriever=retriever,
        ollama=ollama,
        generator=generator,
        ingestion=ingestion,
    )