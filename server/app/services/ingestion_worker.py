
from app.db.main import async_session
from app.services.ingestion import ingest_document


async def ingest_document_background(
    document_id,
):

    async with async_session() as db:

        await ingest_document(
            document_id,
            db,
        )