# app/services/ingestion.py

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_parser import extract_pdf
from app.services.chunker import chunk_text
from app.services.embeddings import generate_embeddings


async def ingest_document(
    document_id,
    db: AsyncSession,
):

    result = await db.execute(
        select(Document).where(
            Document.id == document_id
        )
    )

    document = result.scalar_one()

    try:

        document.status = "processing"

        await db.commit()

        # -----------------------------
        # 1. Extract
        # -----------------------------

        if document.file_type == "application/pdf":

            pages = extract_pdf(
                document.storage_path
            )

        else:

            raise ValueError(
                f"Unsupported file type: "
                f"{document.file_type}"
            )

        document.page_count = len(pages)

        # -----------------------------
        # 2. Chunk
        # -----------------------------

        chunks = chunk_text(pages)

        if not chunks:
            raise ValueError(
                "No text could be extracted "
                "from document."
            )

        # -----------------------------
        # 3. Generate embeddings
        # -----------------------------

        embeddings = await generate_embeddings(
            [
                chunk.content
                for chunk in chunks
            ]
        )

        # -----------------------------
        # 4. Remove old chunks
        # -----------------------------

        await db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id
                == document.id
            )
        )

        # -----------------------------
        # 5. Store chunks
        # -----------------------------

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk.content,
                    embedding=embedding,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    metadata=chunk.metadata,
                )
            )

        document.chunk_count = len(chunks)

        document.status = "ready"
        document.error_message = None

        await db.commit()

    except Exception as exc:

        await db.rollback()

        # Fetch again because rollback
        # invalidates the previous state.
        result = await db.execute(
            select(Document).where(
                Document.id == document_id
            )
        )

        document = result.scalar_one()

        document.status = "failed"
        document.error_message = str(exc)

        await db.commit()

        raise