"""
Async SQLAlchemy engine and session factory.

In production the database URL is read from the DATABASE_URL environment
variable (postgres+asyncpg://...). For tests an in-process SQLite database is
used (sqlite+aiosqlite:///:memory:) by setting DATABASE_URL before the app
starts.
"""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://kwh:kwh@db:5432/kwh",
)

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""


async def get_session() -> AsyncSession:  # type: ignore[return]
    """FastAPI dependency that yields an async DB session.

    Reads AsyncSessionLocal from the module at call time so that test
    fixtures can monkeypatch it and have the change take effect.
    """
    import app.database as _self
    async with _self.AsyncSessionLocal() as session:
        yield session
