# app/api/routes/documents.py

import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
    BackgroundTasks
)
from app.services.ingestion_worker import ingest_document_background
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_db
from app.models.document import Document
from app.models.system import System
from app.services.document_storage import save_upload



docs_router = APIRouter(
    prefix="/systems",
    tags=["Documents"],
)


ALLOWED_TYPES = {
    "application/pdf",
}


@docs_router.post(
    "/{system_id}/documents",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    system_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # 1. Get system
    result = await db.execute(
        select(System).where(System.id == system_id)
    )

    system = result.scalar_one_or_none()

    if not system:
        raise HTTPException(
            status_code=404,
            detail="System not found",
        )

    # 2. Validate file
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported",
        )

    # 3. Create document record
    document = Document(
        id=uuid.uuid4(),
        organization_id=system.organization_id,
        system_id=system.id,
        name=file.filename,
        file_name=file.filename,
        file_type=file.content_type,
        storage_path="",
        status="processing",
    )

    db.add(document)

    # Generate document.id before storage
    await db.flush()

    # 4. Save physical file
    storage_path = await save_upload(
        file=file,
        organization_id=str(system.organization_id),
        system_id=str(system.id),
        document_id=str(document.id),
    )

    document.storage_path = storage_path

    # 5. Persist document
    await db.commit()

    # 6. Start ingestion
    background_tasks.add_task(
        ingest_document_background,
        document.id,
    )

    return {
        "id": str(document.id),
        "file_name": document.file_name,
        "status": document.status,
    }

@docs_router.get(
    "/documents/{document_id}",
)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Document).where(
            Document.id == document_id
        )
    )

    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "id": str(document.id),
        "name": document.file_name,
        "status": document.status,
        "pages": document.page_count,
        "chunks": document.chunk_count,
        "error": document.error_message,
    }

@docs_router.get("/{system_id}/documents")
async def get_documents_by_system(
    system_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # Verify system exists
    result = await db.execute(
        select(System).where(System.id == system_id)
    )

    system = result.scalar_one_or_none()

    if not system:
        raise HTTPException(
            status_code=404,
            detail="System not found",
        )

    # Get documents belonging to the system
    result = await db.execute(
        select(Document)
        .where(Document.system_id == system_id)
        .order_by(Document.created_at.desc())
    )

    documents = result.scalars().all()

    return documents