import time
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request

from backend.models import (
    ChatRequest,
    ChatResponse,
    Source,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: Request,
    body: ChatRequest,
):

    total_start = time.perf_counter()

    query = body.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )
    conversation_id = body.conversation_id
    chat_history = request.app.state.chat_history

    if conversation_id:
        try:
            UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid conversation ID.",
            )

        existing_messages = await chat_history.get_messages(conversation_id)

        if existing_messages is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        await chat_history.add_message(
            conversation_id=conversation_id,
            role="user",
            content=query,
        )

    state = request.app.state.rag

    top_k = body.top_k or 5

    retrieval_start = time.perf_counter()

    chunks = state.retriever.retrieve(
        query=query,
        top_k=top_k,
    )

    retrieval_ms = (
        time.perf_counter() - retrieval_start
    ) * 1000

    generation_start = time.perf_counter()

    answer, retrieved_chunks = (
        await state.generator.generate(
            query=query,
            chunks=chunks,
        )
    )

    generation_ms = (
        time.perf_counter() - generation_start
    ) * 1000

    total_ms = (
        time.perf_counter() - total_start
    ) * 1000

    sources = [
        Source(
            document_name=chunk.document_name,
            page_number=chunk.page_number,
            chunk_id=chunk.chunk_id,
            score=chunk.score,
        )
        for chunk in retrieved_chunks
    ]

    latency = {
        "retrieval_ms": round(retrieval_ms, 2),
        "generation_ms": round(generation_ms, 2),
        "total_ms": round(total_ms, 2),
    }

    if conversation_id:
        await chat_history.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            sources=[source.model_dump() for source in sources],
            latency=latency,
        )
        
    print(
        f"[CHAT] "
        f"retrieval={retrieval_ms:.2f}ms "
        f"generation={generation_ms:.2f}ms "
        f"total={total_ms:.2f}ms "
        f"chunks={len(chunks)}"
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
        latency=latency,
    )