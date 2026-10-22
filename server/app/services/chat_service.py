import logging
import re
import uuid
from datetime import datetime
from collections.abc import AsyncIterator
from dataclasses import dataclass

from agents import RunConfig, Runner
from agents.exceptions import MaxTurnsExceeded
from fastapi import HTTPException
from openai.types.responses import ResponseTextDeltaEvent
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.agents.context import AgentContext
from app.agents.support_agent import support_agent
from app.core.chat_config import HISTORY_LIMIT, MAX_TURNS
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatResponse, ConversationDetail, MessageOut, SourceRef

logger = logging.getLogger(__name__)

CITATION_RE = re.compile(r"\[(S\d+)\]")
FALLBACK_ANSWER = "I couldn't put together an answer. Please try rephrasing, or contact IT support."


@dataclass
class Turn:
    conversation_id: uuid.UUID
    message: str
    history: list[dict[str, str]]


def _strip_citations(text: str) -> str:
    """Source IDs are only valid within the turn that produced them."""
    return CITATION_RE.sub("", text).replace("  ", " ").strip()


async def _owned_conversation(db: AsyncSession, user, conversation_id: uuid.UUID) -> Conversation:
    """Fetch a conversation only if it belongs to this user and org; otherwise 404
    (404 rather than 403 so IDs of other tenants' conversations aren't confirmed)."""
    conv = await db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == user.organization_id,
            Conversation.user_id == user.id,
        )
    )
    if conv is None:
        raise HTTPException(404, "Conversation not found")
    return conv


async def prepare_turn(
    db: AsyncSession, user, message: str, conversation_id: uuid.UUID | None
) -> Turn:
    """Runs BEFORE streaming starts, so failures can still return proper HTTP codes."""
    if conversation_id:
        conv = await _owned_conversation(db, user, conversation_id)
        rows = (
            await db.scalars(
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.desc())
                .limit(HISTORY_LIMIT)
            )
        ).all()
        history = [
            {"role": m.role, "content": _strip_citations(m.content)} for m in reversed(rows)
        ]
    else:
        conv = Conversation(
            organization_id=user.organization_id, user_id=user.id, title=message[:80]
        )
        db.add(conv)
        await db.flush()
        history = []

    db.add(Message(conversation_id=conv.id, role="user", content=message))
    conv.updated_at = datetime.utcnow()
    await db.commit()
    return Turn(conversation_id=conv.id, message=message, history=history)


def _cited_sources(answer: str, ctx: AgentContext) -> list[SourceRef]:
    """Return only sources the answer actually cites (and that really exist)."""
    seen: list[str] = []
    for sid in CITATION_RE.findall(answer):
        if sid in ctx.sources and sid not in seen:
            seen.append(sid)
    return [
        SourceRef(
            id=s.id,
            document_id=s.document_id,
            title=s.title,
            page_number=s.page_number,
            snippet=s.content[:240],
            score=round(s.score, 3),
        )
        for s in (ctx.sources[i] for i in seen)
    ]


async def run_turn(
    turn: Turn, user, session_factory: async_sessionmaker[AsyncSession]
) -> AsyncIterator[tuple[str, dict]]:
    """Yields (event_name, payload): status | token | done | error."""
    ctx = AgentContext(
        organization_id=user.organization_id,
        user_id=user.id,
        session_factory=session_factory,
    )
    agent_input = [*turn.history, {"role": "user", "content": turn.message}]

    try:
        result = Runner.run_streamed(
            support_agent,
            agent_input,
            context=ctx,
            max_turns=MAX_TURNS,
            run_config=RunConfig(
                workflow_name="support_chat",
                group_id=str(turn.conversation_id),
                trace_include_sensitive_data=False,
            ),
        )
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                yield "token", {"text": event.data.delta}
            elif event.type == "run_item_stream_event" and event.name == "tool_called":
                yield "status", {"state": "searching"}
        answer = (result.final_output or "").strip() or FALLBACK_ANSWER
    except MaxTurnsExceeded:
        logger.warning("max turns exceeded conversation=%s", turn.conversation_id)
        yield "error", {"message": "That took too many steps. Please rephrase or narrow the question."}
        return
    except Exception:
        logger.exception("agent run failed conversation=%s", turn.conversation_id)
        yield "error", {"message": "Something went wrong. Please try again."}
        return

    sources = _cited_sources(answer, ctx)
    message_id = uuid.uuid4()
    try:
        async with session_factory() as db:
            db.add(
                Message(
                    id=message_id,
                    conversation_id=turn.conversation_id,
                    role="assistant",
                    content=answer,
                    sources=[s.model_dump(mode="json") for s in sources],
                )
            )
            await db.execute(
                update(Conversation)
                .where(Conversation.id == turn.conversation_id)
                .values(updated_at=datetime.utcnow())
            )
            await db.commit()
    except Exception:
        logger.exception("failed to persist assistant message")

    yield "done", ChatResponse(
        conversation_id=turn.conversation_id,
        message_id=message_id,
        answer=answer,
        sources=sources,
    ).model_dump(mode="json")


async def list_conversations(
    db: AsyncSession, user, limit: int = 20, offset: int = 0
) -> list[Conversation]:
    return list(
        (
            await db.scalars(
                select(Conversation)
                .where(
                    Conversation.organization_id == user.organization_id,
                    Conversation.user_id == user.id,
                )
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
        ).all()
    )


async def get_conversation(
    db: AsyncSession, user, conversation_id: uuid.UUID
) -> ConversationDetail:
    conv = await _owned_conversation(db, user, conversation_id)
    rows = (
        await db.scalars(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
        )
    ).all()
    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageOut.model_validate(m) for m in rows],
    )


async def delete_conversation(db: AsyncSession, user, conversation_id: uuid.UUID) -> None:
    conv = await _owned_conversation(db, user, conversation_id)
    await db.execute(
        delete(Message).where(Message.conversation_id == conv.id)
    )
    await db.execute(delete(Conversation).where(Conversation.id == conv.id))
    await db.commit()