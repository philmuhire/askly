from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.models.system import System
from app.services.embeddings import generate_embeddings


async def search_knowledge(
    db: AsyncSession,
    organization_id,
    query: str,
    limit: int = 5,
):

    # Embed question
    embeddings = await generate_embeddings(
        [query]
    )

    query_embedding = embeddings[0]

    # Vector similarity
    distance = (
        DocumentChunk.embedding.cosine_distance(
            query_embedding
        )
    )

    stmt = (
        select(
            DocumentChunk,
            Document,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .join(
            System,
            System.id
            == Document.system_id,
        )
        .where(
            System.organization_id
            == organization_id
        )
        .order_by(distance)
        .limit(limit)
    )

    result = await db.execute(stmt)

    return result.all()