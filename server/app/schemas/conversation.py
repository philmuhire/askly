# app/schemas/conversation.py

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    system_id: UUID
    title: str | None = None


class ConversationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    system_id: UUID
    user_id: UUID
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }