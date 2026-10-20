
from dataclasses import dataclass

from backend.answer_generator import AnswerGenerator
from backend.embeddings_dense import DenseEmbedder
from backend.embeddings_splade import SpladeEmbedder
from backend.ingestion_pipeline import IngestionPipeline
from backend.ollama_client import OllamaClient
from backend.qdrant_client import QdrantVectorStore
from backend.retreiver_dense import DenseRetriever
from backend.retriever_hybrid import HybridRetriever
from backend.retriever_splade import SpladeRetriever


@dataclass
class AppState:
    embedder: DenseEmbedder
    splade_embedder: SpladeEmbedder
    qdrant: QdrantVectorStore
    dense_retriever: DenseRetriever
    splade_retriever: SpladeRetriever
    retriever: HybridRetriever
    ollama: OllamaClient
    generator: AnswerGenerator
    ingestion: IngestionPipeline


def create_app_state() -> AppState:
    embedder = DenseEmbedder()
    splade_embedder = SpladeEmbedder()
    qdrant = QdrantVectorStore()

    qdrant.create_collection(
        vector_size=embedder.dimension
    )

    dense_retriever = DenseRetriever(
        embedder=embedder,
        vector_store=qdrant,
    )

    splade_retriever = SpladeRetriever(
        embedder=splade_embedder,
        vector_store=qdrant,
    )

    retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        splade_retriever=splade_retriever,
        vector_store=qdrant,
        rrf_k=60,
        candidate_limit=30,
    )

    ollama = OllamaClient()

    generator = AnswerGenerator(
        ollama_client=ollama,
    )

    ingestion = IngestionPipeline(
        embedder=embedder,
        vector_store=qdrant,
        splade_embedder=splade_embedder,
    )

    return AppState(
        embedder=embedder,
        splade_embedder=splade_embedder,
        qdrant=qdrant,
        dense_retriever=dense_retriever,
        splade_retriever=splade_retriever,
        retriever=retriever,
        ollama=ollama,
        generator=generator,
        ingestion=ingestion,
    )
