from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True)

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )

    system_id = Column(
        UUID(as_uuid=True),
        ForeignKey("systems.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Document metadata
    name = Column(String, nullable=False)
    description = Column(Text)

    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)

    # Document versioning
    version = Column(String)

    # Ingestion state
    status = Column(
        String,
        nullable=False,
        default="processing",
    )

    page_count = Column(Integer)
    chunk_count = Column(Integer)

    error_message = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
    )

    organization = relationship(
        "Organization",
        back_populates="documents",
    )

    system = relationship(
        "System",
        back_populates="documents",
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )