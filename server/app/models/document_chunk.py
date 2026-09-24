from sqlalchemy import Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True)

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    content = Column(Text, nullable=False)

    embedding = Column(Vector(1536))

    chunk_index = Column(Integer)

    page_number = Column(Integer)

    #     metadata is a dictionary of metadata about the chunk
    #     {
    #   "section": "Purchase Requests",
    #   "subsection": "Creating a Request",
    #   "page": 42,
    #   "document_version": "2.4",
    #   "language": "en",
    #   "content_type": "procedure"
    # }
    metadata = Column(JSONB)

    document = relationship("Document", back_populates="chunks")
