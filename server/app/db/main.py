import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base  # re-exported for convenience

from dotenv import load_dotenv
from app.core.config import settings
load_dotenv()

DATABASE_URL = settings.database_url

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=True,
    expire_on_commit=False
)


async def get_db():
    async with async_session() as session:
        yield session
