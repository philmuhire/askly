from sqlalchemy import Column, DateTime, String, Text, ForeignKey
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
        ForeignKey("systems.id"),
        nullable=True
    )

    name = Column(String, nullable=False)
    description = Column(Text)

    file_name = Column(String)
    file_type = Column(String)
    file_path = Column(String)

    version = Column(String)
    status = Column(String, default="processing")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
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