import logging
import time
from typing import List

from backend.embeddings_splade import SpladeEmbedder
from backend.models import RetrievedChunk
from backend.qdrant_client import QdrantVectorStore

logger = logging.getLogger(__name__)


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
        total_start = time.perf_counter()

        encode_start = time.perf_counter()
        indices, values = self.embedder.encode_query(query)
        encode_ms = (time.perf_counter() - encode_start) * 1000

        if not indices or not values:
            logger.info(
                "SPLADE timing | encode=%.2f ms | qdrant=0.00 ms | total=%.2f ms",
                encode_ms,
                (time.perf_counter() - total_start) * 1000,
            )
            return []

        search_start = time.perf_counter()
        results = self.vector_store.search_sparse(
            indices=indices,
            values=values,
            limit=top_k,
        )
        search_ms = (time.perf_counter() - search_start) * 1000

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

        total_ms = (time.perf_counter() - total_start) * 1000

        logger.info(
            "SPLADE timing | encode=%.2f ms | qdrant=%.2f ms | processing=%.2f ms | total=%.2f ms | results=%d",
            encode_ms,
            search_ms,
            max(0.0, total_ms - encode_ms - search_ms),
            total_ms,
            len(chunks),
        )

        return chunks