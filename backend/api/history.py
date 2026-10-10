
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/conversations",
    tags=["Chat History"],
)


class ConversationCreate(BaseModel):
    title: str = Field(default="New chat", max_length=80)


@router.post("")
async def create_conversation(
    body: ConversationCreate,
    request: Request,
):
    title = body.title.strip() or "New chat"

    conversation_id = await request.app.state.chat_history.create_conversation(
        title
    )

    return {"id": conversation_id, "title": title}


@router.get("")
async def list_conversations(request: Request):
    conversations = await request.app.state.chat_history.list_conversations()

    return {"conversations": conversations}


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    request: Request,
):
    try:
        UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID.",
        )

    messages = await request.app.state.chat_history.get_messages(
        conversation_id
    )

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return {
        "conversation_id": conversation_id,
        "messages": messages,
    }


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    request: Request,
):
    deleted = await request.app.state.chat_history.delete_conversation(
        conversation_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return {"status": "success"}
