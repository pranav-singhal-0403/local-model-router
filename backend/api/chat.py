from fastapi import APIRouter, HTTPException, Request
from backend.models import ChatRequest, ChatResponse, Source

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
async def chat(
    request: Request,
    body: ChatRequest,
):

    query = body.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )
    state = request.app.state.rag
    top_k = body.top_k or 5

    chunks = state.retriever.retrieve(
        query=query,
        top_k=top_k,
    )

    answer, retrieved_chunks = (
        await state.generator.generate(
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