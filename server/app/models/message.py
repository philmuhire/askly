"""Message model matching your existing Conversation.messages relationship.

If you already have a Message model, keep yours and just make sure it has:
conversation_id, role, content, created_at, and the nullable JSONB `sources` column.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)

    # Citations shown to the user for assistant messages: [{id, document_id, title, ...}]
    sources = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    conversation = relationship("Conversation", back_populates="messages")