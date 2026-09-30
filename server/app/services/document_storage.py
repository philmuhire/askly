# app/services/document_storage.py

from pathlib import Path
import shutil

from fastapi import UploadFile


STORAGE_ROOT = Path("storage")


async def save_upload(
    file: UploadFile,
    organization_id: str,
    system_id: str,
    document_id: str,
) -> str:

    directory = (
        STORAGE_ROOT
        / organization_id
        / system_id
        / document_id
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = directory / file.filename

    with path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    return str(path)