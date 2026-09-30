from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key
)


EMBEDDING_MODEL = "text-embedding-3-small"


async def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:

    embeddings: list[list[float]] = []

    # Batch requests.
    batch_size = 100

    for i in range(0, len(texts), batch_size):

        batch = texts[i:i + batch_size]

        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )

        embeddings.extend(
            item.embedding
            for item in response.data
        )

    return embeddings