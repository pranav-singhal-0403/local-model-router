from fastapi import APIRouter, HTTPException

from backend.answer_generator import AnswerGenerator
from backend.models import ChatRequest, ChatResponse, Source
from backend.retreiver_dense import DenseRetriever


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
):

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    retriever = DenseRetriever()

    top_k = request.top_k or 5

    chunks = retriever.retrieve(
        query=query,
        top_k=top_k,
    )

    generator = AnswerGenerator()

    answer, retrieved_chunks = (
        await generator.generate(
            query=query,
            chunks=chunks,
        )
    )

    sources = [
        Source(
            document_name=chunk.document_name,
            page_number=chunk.page_number,
            chunk_id=chunk.chunk_id,
            score=chunk.score,
        )
        for chunk in retrieved_chunks
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
    )