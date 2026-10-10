from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
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

    def list_documents(self):
        documents = {}
        offset = None

        while True:
            records, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                offset=offset,
                limit=256,
                with_payload=True,
                with_vectors=False,
            )

            for record in records:
                payload = record.payload or {}
                document_id = payload.get("document_id")

                if not document_id:
                    continue

                if document_id not in documents:
                    documents[document_id] = {
                        "document_id": document_id,
                        "document_name": payload.get(
                            "document_name",
                            "Unknown document",
                        ),
                        "stored_filename": payload.get(
                            "stored_filename",
                            payload.get("document_name", ""),
                        ),
                        "chunks": 0,
                        "pages": set(),
                    }

                document = documents[document_id]
                document["chunks"] += 1

                page_number = payload.get("page_number")

                if page_number is not None:
                    document["pages"].add(page_number)

            if next_offset is None:
                break

            offset = next_offset

        result = []

        for document in documents.values():
            document["pages"] = len(document["pages"])
            result.append(document)

        return sorted(
            result,
            key=lambda document: document["document_name"].lower(),
        )

    def delete_document(self, document_id: str):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                )
            ),
            wait=True,
        )