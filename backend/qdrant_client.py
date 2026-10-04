from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from backend.config import (
    QDRANT_COLLECTION,
    QDRANT_HOST,
    QDRANT_PORT,
)


class QdrantVectorStore:

    def __init__(self):
        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        self.collection_name = QDRANT_COLLECTION

    def collection_exists(self) -> bool:
        collections = self.client.get_collections()

        return any(
            collection.name == self.collection_name
            for collection in collections.collections
        )

    def create_collection(self, vector_size: int):
        if self.collection_exists():
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    def upsert(
        self,
        points: List[PointStruct],
    ):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
    ):
        return self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        ).points