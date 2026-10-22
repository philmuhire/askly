from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    """Note: no tenant/org id here. It always comes from the authenticated user."""

    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None

    @field_validator("message")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message must not be blank")
        return v


class SourceRef(BaseModel):
    id: str            # e.g. "S1", valid only within the answer it came with
    document_id: UUID
    title: str
    page_number: int | None = None
    snippet: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    answer: str
    sources: list[SourceRef]


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    sources: list[SourceRef] | None = None
    created_at: datetime


class ConversationDetail(ConversationSummary):
    messages: list[MessageOut]