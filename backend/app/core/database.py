"""Async SQLAlchemy database engine and session factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_size=10, max_overflow=20)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """FastAPI dependency: yields an async database session.

    The session is automatically closed when the request completes.
    Routes are responsible for calling commit() explicitly.
    If an unhandled exception occurs, the transaction is implicitly rolled back.
    """
    async with async_session_factory() as session:
        yield session
