from pathlib import Path
from uuid import uuid4

from qdrant_client.models import PointStruct

from backend.config import (
    CHUNKING_CONFIG,
)

from backend.embeddings_dense import DenseEmbedder
from backend.chunker import split_into_chunks
from backend.pdf_parser import parse_pdf
from backend.models import DocumentChunk
from backend.qdrant_client import QdrantVectorStore


class IngestionPipeline:

    def __init__(
        self,
        embedder: DenseEmbedder,
        vector_store: QdrantVectorStore,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.vector_store.create_collection(
            vector_size=self.embedder.dimension
        )

    def ingest_pdf(
        self,
        pdf_path: Path,
        display_name: str | None = None,
    ):

        document_id = str(uuid4())
        document_name = display_name or pdf_path.name
        pages = parse_pdf(pdf_path)

        chunks = []

        target_words = max(
            1,
            int(
                CHUNKING_CONFIG["target_tokens"] * 0.75
            ),
        )

        overlap_words = max(
            1,
            int(
                CHUNKING_CONFIG["overlap_tokens"] * 0.75
            ),
        )

        chunk_index = 0

        for page in pages:

            page_chunks = split_into_chunks(
                page["text"],
                target_words=target_words,
                overlap_words=overlap_words,
            )

            for chunk_text in page_chunks:

                chunk = DocumentChunk(
                    chunk_id=str(uuid4()),
                    document_id=document_id,
                    document_name=document_name,
                    page_number=page["page_number"],
                    chunk_index=chunk_index,
                    text=chunk_text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page["page_number"],
                        "document_id": document_id,
                        "document_name": document_name,
                        "stored_filename": pdf_path.name,
                    },
                )

                chunks.append(chunk)

                chunk_index += 1

        if not chunks:
            raise ValueError(
                "No text could be extracted from the PDF."
            )

        embeddings = self.embedder.encode(
            [chunk.text for chunk in chunks]
        )

        points = []

        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                PointStruct(
                    id=chunk.chunk_id,
                    vector=embedding,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "document_id": chunk.document_id,
                        "document_name": chunk.document_name,
                        "stored_filename": pdf_path.name,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "metadata": chunk.metadata,
                    },
                )
            )

        self.vector_store.upsert(points)

        return {
            "document_id": document_id,
            "document_name": document_name,
            "stored_filename": pdf_path.name,
            "pages": len(pages),
            "chunks": len(chunks),
        }