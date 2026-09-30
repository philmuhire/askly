# app/services/chunker.py

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    page_number: int | None
    section: str | None
    metadata: dict


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def chunk_text(
    pages: list[dict],
    chunk_size: int = 3000,
    overlap: int = 400,
) -> list[Chunk]:

    chunks: list[Chunk] = []

    for page in pages:

        text = clean_text(page["text"])

        if not text:
            continue

        start = 0

        while start < len(text):

            end = min(
                start + chunk_size,
                len(text),
            )

            chunk = text[start:end]

            # Try not to cut a sentence in half.
            if end < len(text):
                last_period = chunk.rfind(".")

                if last_period > chunk_size * 0.6:
                    chunk = chunk[: last_period + 1]
                    end = start + len(chunk)

            chunk = chunk.strip()

            if chunk:
                chunks.append(
                    Chunk(
                        content=chunk,
                        page_number=page["page_number"],
                        section=None,
                        metadata={
                            "page": page["page_number"],
                        },
                    )
                )

            if end >= len(text):
                break

            start = max(
                end - overlap,
                start + 1,
            )

    return chunks