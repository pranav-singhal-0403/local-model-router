
from concurrent.futures import ThreadPoolExecutor
from typing import List

from backend.models import RetrievedChunk
from backend.retreiver_dense import DenseRetriever
from backend.retriever_splade import SpladeRetriever
from backend.qdrant_client import QdrantVectorStore


class HybridRetriever:
    def __init__(
        self,
        dense_retriever: DenseRetriever,
        splade_retriever: SpladeRetriever,
        vector_store: QdrantVectorStore,
        rrf_k: int = 60,
        candidate_limit: int = 30,
    ):
        self.dense_retriever = dense_retriever
        self.splade_retriever = splade_retriever
        self.vector_store = vector_store
        self.rrf_k = rrf_k
        self.candidate_limit = candidate_limit
        self.executor = ThreadPoolExecutor(max_workers=2)

    @staticmethod
    def deduplicate(
        chunks: List[RetrievedChunk],
    ) -> List[RetrievedChunk]:
        unique = {}
        for chunk in chunks:
            unique.setdefault(chunk.chunk_id, chunk)
        return list(unique.values())

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[RetrievedChunk]:
        candidate_limit = max(self.candidate_limit, top_k)

        dense_future = self.executor.submit(
            self.dense_retriever.retrieve,
            query=query,
            top_k=candidate_limit,
        )
        splade_future = self.executor.submit(
            self.splade_retriever.retrieve,
            query=query,
            top_k=candidate_limit,
        )

        dense_results = self.deduplicate(dense_future.result())
        splade_results = self.deduplicate(splade_future.result())

        fused_scores = {}
        chunks_by_id = {}

        for ranked_results in (dense_results, splade_results):
            for rank, chunk in enumerate(ranked_results, start=1):
                chunk_id = chunk.chunk_id
                fused_scores[chunk_id] = (
                    fused_scores.get(chunk_id, 0.0)
                    + 1.0 / (self.rrf_k + rank)
                )
                chunks_by_id.setdefault(chunk_id, chunk)

        ranked_ids = sorted(
            fused_scores,
            key=lambda chunk_id: fused_scores[chunk_id],
            reverse=True,
        )

        return [
            RetrievedChunk(
                chunk_id=chunks_by_id[chunk_id].chunk_id,
                document_id=chunks_by_id[chunk_id].document_id,
                document_name=chunks_by_id[chunk_id].document_name,
                page_number=chunks_by_id[chunk_id].page_number,
                text=chunks_by_id[chunk_id].text,
                score=fused_scores[chunk_id],
                metadata=chunks_by_id[chunk_id].metadata,
            )
            for chunk_id in ranked_ids[:top_k]
        ]
