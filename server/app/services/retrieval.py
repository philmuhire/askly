import logging
from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.chat_config import (
    RETRIEVAL_MAX_PER_DOCUMENT,
    RETRIEVAL_MIN_SIMILARITY,
    RETRIEVAL_TOP_K,
)
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.system import System
from app.services.embeddings import generate_embeddings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: UUID
    document_id: UUID
    document_title: str
    content: str
    score: float  # cosine similarity, higher is better
    page_number: int | None = None


async def search_knowledge(
    db: AsyncSession,
    organization_id: UUID,
    query: str,
    *,
    limit: int = RETRIEVAL_TOP_K,
    min_similarity: float = RETRIEVAL_MIN_SIMILARITY,
    max_per_document: int = RETRIEVAL_MAX_PER_DOCUMENT,
) -> list[RetrievedChunk]:
    """Tenant-scoped vector search with a relevance floor and per-document diversity."""
    query = query.strip()
    if not query:
        return []

    [query_embedding] = await generate_embeddings([query])
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(
            DocumentChunk.id.label("chunk_id"),
            DocumentChunk.document_id.label("document_id"),
            DocumentChunk.content.label("content"),
            DocumentChunk.page_number.label("page_number"),
            Document.name.label("name"),
            distance.label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .join(System, System.id == Document.system_id)
        .where(System.organization_id == organization_id)  # tenant isolation
        .order_by(distance)
        .limit(limit * 4)  # over-fetch so diversity filtering still fills `limit`
    )
    rows = (await db.execute(stmt)).all()

    results: list[RetrievedChunk] = []
    per_doc: dict[UUID, int] = defaultdict(int)
    for row in rows:  # sorted by distance ascending
        score = 1.0 - float(row.distance)
        if score < min_similarity:
            break
        if per_doc[row.document_id] >= max_per_document:
            continue
        per_doc[row.document_id] += 1
        results.append(
            RetrievedChunk(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                document_title=row.name,
                content=row.content,
                score=score,
                page_number=row.page_number,
            )
        )
        if len(results) >= limit:
            break

    logger.info("retrieval org=%s returned=%d top=%.3f", organization_id, len(results),
                results[0].score if results else 0.0)
    print(results)
    return results