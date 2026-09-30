from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True)

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False
    )

    system_id = Column(
        UUID(as_uuid=True),
        ForeignKey("systems.id", ondelete="CASCADE"),
        nullable=True
    )

    name = Column(String, nullable=False)
    description = Column(Text)

    file_name = Column(String)
    file_type = Column(String)
    file_path = Column(String)

    version = Column(String)
    status = Column(String, default="processing")
    page_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    organization = relationship(
        "Organization",
        back_populates="documents"
    )

    system = relationship(
        "System",
        back_populates="documents"
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document"
    )