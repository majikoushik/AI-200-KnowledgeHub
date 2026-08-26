from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()


# ---------------------------------------------------------
# Engine
# ---------------------------------------------------------

engine = create_async_engine(
    settings.database_url,
    echo=settings.sql_echo,
    pool_pre_ping=True,
)


# ---------------------------------------------------------
# Session factory
# ---------------------------------------------------------

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------


async def get_db_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:

    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------


async def check_database_connection() -> None:

    async with engine.connect() as connection:

        await connection.execute(text("SELECT 1"))


# ---------------------------------------------------------
# Shutdown
# ---------------------------------------------------------


async def close_database() -> None:

    await engine.dispose()
