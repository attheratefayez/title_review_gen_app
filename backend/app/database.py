import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DB_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./data.db")

engine = create_async_engine(DB_URL, echo=False)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


# yield the session and when that goes out of scope close the session
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
