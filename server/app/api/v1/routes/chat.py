import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.main import async_session, get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
)
from app.services import chat_service
from app.services.chat_service import prepare_turn, run_turn

chat_router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@chat_router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Non-streaming: returns the complete answer with cited sources."""
    turn = await prepare_turn(db, user, body.message, body.conversation_id)
    async for event, data in run_turn(turn, user, async_session):
        if event == "error":
            raise HTTPException(status_code=502, detail=data["message"])
        if event == "done":
            return ChatResponse(**data)
    raise HTTPException(status_code=500, detail="No response produced")


@chat_router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SSE: `meta` (conversation_id), `status`, `token`*, then `done` or `error`."""
    turn = await prepare_turn(db, user, body.message, body.conversation_id)

    async def gen():
        # Sent first so the client knows the id of a brand-new conversation immediately.
        yield _sse("meta", {"conversation_id": str(turn.conversation_id)})
        async for event, data in run_turn(turn, user, async_session):
            yield _sse(event, data)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@chat_router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.list_conversations(db, user, limit, offset)


@chat_router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.get_conversation(db, user, conversation_id)


@chat_router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await chat_service.delete_conversation(db, user, conversation_id)
    return Response(status_code=204)