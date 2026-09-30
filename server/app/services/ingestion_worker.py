
from app.db.main import get_db
from app.services.ingestion import ingest_document


async def ingest_document_background(
    document_id,
):

    async with get_db() as db:

        await ingest_document(
            document_id,
            db,
        )