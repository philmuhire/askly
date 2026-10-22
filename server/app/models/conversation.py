
import uuid

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    system_id = Column(
        UUID(as_uuid=True),
        ForeignKey("systems.id", ondelete="CASCADE"),
        nullable=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="active",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )