
from typing import List

from backend.embeddings_splade import SpladeEmbedder
from backend.models import RetrievedChunk
from backend.qdrant_client import QdrantVectorStore


class SpladeRetriever:
    def __init__(
        self,
        embedder: SpladeEmbedder,
        vector_store: QdrantVectorStore,
    ):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 30,
    ) -> List[RetrievedChunk]:
        indices, values = self.embedder.encode_query(query)

        if not indices or not values:
            return []

        results = self.vector_store.search_sparse(
            indices=indices,
            values=values,
            limit=top_k,
        )

        chunks = []

        for result in results:
            payload = result.payload or {}

            if not payload.get("chunk_id"):
                continue

            chunks.append(
                RetrievedChunk(
                    chunk_id=str(payload["chunk_id"]),
                    document_id=str(payload["document_id"]),
                    document_name=str(payload["document_name"]),
                    page_number=int(payload["page_number"]),
                    text=str(payload["text"]),
                    score=float(result.score),
                    metadata=payload.get("metadata", {}),
                )
            )

        return chunks
