from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.retrieval import RetrievedChunk


@dataclass
class Source:
    id: str
    chunk_id: UUID
    document_id: UUID
    title: str
    content: str
    score: float
    page_number: int | None = None


@dataclass
class AgentContext:
    """Per-run state. Never visible to the model; tools read identity from here,
    so the LLM can't choose which tenant it searches."""

    organization_id: UUID
    user_id: UUID
    # A factory (not a session): tools may run in parallel and an AsyncSession
    # must not be shared between concurrent tasks.
    session_factory: async_sessionmaker[AsyncSession]
    sources: dict[str, Source] = field(default_factory=dict)
    _by_chunk: dict[UUID, Source] = field(default_factory=dict)

    def register(self, chunk: RetrievedChunk) -> Source:
        if chunk.chunk_id in self._by_chunk:
            return self._by_chunk[chunk.chunk_id]
        src = Source(
            id=f"S{len(self.sources) + 1}",
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            title=chunk.document_title,
            content=chunk.content,
            score=chunk.score,
            page_number=chunk.page_number,
        )
        self.sources[src.id] = src
        self._by_chunk[chunk.chunk_id] = src
        return src