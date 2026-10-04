from typing import List

from backend.embeddings_dense import DenseEmbedder
from backend.models import RetrievedChunk
from backend.qdrant_client import QdrantVectorStore


class DenseRetriever:

    def __init__(
        self,
        embedder: DenseEmbedder,
        vector_store: QdrantVectorStore,
    ):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[RetrievedChunk]:

        query_vector = self.embedder.encode_query(
            query
        )

        results = self.vector_store.search(
            query_vector=query_vector,
            limit=top_k,
        )

        retrieved_chunks = []

        for result in results:

            payload = result.payload or {}

            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=payload["chunk_id"],
                    document_id=payload["document_id"],
                    document_name=payload["document_name"],
                    page_number=payload["page_number"],
                    text=payload["text"],
                    score=float(result.score),
                    metadata=payload.get(
                        "metadata",
                        {},
                    ),
                )
            )

        return retrieved_chunks