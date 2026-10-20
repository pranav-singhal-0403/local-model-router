
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from backend.config import QDRANT_HOST, QDRANT_PORT
from backend.embeddings_dense import DenseEmbedder
from backend.embeddings_splade import SpladeEmbedder


SOURCE_COLLECTION = "rag_documents"
TARGET_COLLECTION = "rag_documents_splade_test"
BATCH_SIZE = 32


def main():
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
    )

    source_info = client.get_collection(SOURCE_COLLECTION)
    target_exists = any(
        collection.name == TARGET_COLLECTION
        for collection in client.get_collections().collections
    )

    if target_exists:
        raise RuntimeError(
            f"{TARGET_COLLECTION} already exists. "
            "Inspect it before migrating; this script will not overwrite it."
        )

    dense_embedder = DenseEmbedder()
    splade_embedder = SpladeEmbedder()

    client.create_collection(
        collection_name=TARGET_COLLECTION,
        vectors_config={
            "dense": VectorParams(
                size=dense_embedder.dimension,
                distance=Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "splade": SparseVectorParams(
                index=SparseIndexParams(on_disk=False)
            )
        },
    )

    offset = None
    migrated = 0

    try:
        while True:
            records, next_offset = client.scroll(
                collection_name=SOURCE_COLLECTION,
                offset=offset,
                limit=BATCH_SIZE,
                with_payload=True,
                with_vectors=True,
            )

            if not records:
                break

            texts = [
                str((record.payload or {}).get("text", ""))
                for record in records
            ]

            dense_vectors = dense_embedder.encode(texts)
            sparse_vectors = splade_embedder.encode(texts)

            points = []

            for record, text, dense_vector, sparse_vector in zip(
                records,
                texts,
                dense_vectors,
                sparse_vectors,
            ):
                if not text.strip():
                    continue

                indices, values = sparse_vector

                points.append(
                    PointStruct(
                        id=record.id,
                        vector={
                            "dense": dense_vector,
                            "splade": SparseVector(
                                indices=indices,
                                values=values,
                            ),
                        },
                        payload=record.payload or {},
                    )
                )

            if points:
                client.upsert(
                    collection_name=TARGET_COLLECTION,
                    points=points,
                    wait=True,
                )
                migrated += len(points)

            print(f"Migrated {migrated} chunks")

            if next_offset is None:
                break

            offset = next_offset

        target_info = client.get_collection(TARGET_COLLECTION)

        print(f"Source collection: {SOURCE_COLLECTION}")
        print(f"Target collection: {TARGET_COLLECTION}")
        print(f"Source points: {source_info.points_count}")
        print(f"Migrated points: {migrated}")
        print(f"Target points: {target_info.points_count}")

        if migrated != source_info.points_count:
            raise RuntimeError(
                "Migration count mismatch. Inspect the target collection "
                "before running evaluation."
            )

    finally:
        client.close()


if __name__ == "__main__":
    main()
