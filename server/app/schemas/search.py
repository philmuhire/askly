from pydantic import BaseModel
from uuid import UUID


class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 5


class KnowledgeSearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_name: str
    content: str
    distance: float