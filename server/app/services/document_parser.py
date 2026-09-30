# app/services/document_parser.py

from pathlib import Path

from pypdf import PdfReader


def extract_pdf(path: str) -> list[dict]:
    reader = PdfReader(path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        text = text.strip()

        if not text:
            continue

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    return pages