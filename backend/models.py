from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    chunk_index: int
    text: str

    metadata: dict = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    text: str
    score: float
    metadata: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    conversation_id: Optional[str] = None


class Source(BaseModel):
    document_name: str
    page_number: int
    chunk_id: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]