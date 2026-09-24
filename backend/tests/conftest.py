"""
Shared test fixtures for kwh-meter backend tests.

Tests use an in-memory SQLite database (via aiosqlite) to avoid needing
a running PostgreSQL instance. The DATABASE_URL env var is overridden
before the app module is imported so SQLAlchemy picks up the test URL.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

VALID_METER_DATA: dict[str, str] = {
    "zaehler_nr": "DE00012345678901234567890",
    "street": "Musterstraße",
    "house_number": "42",
    "postal_code": "12345",
    "city": "Musterstadt",
}


@pytest.fixture()
def valid_meter_config_file() -> Any:
    """Write a valid meter config JSON file and return its path."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as fh:
        json.dump(VALID_METER_DATA, fh)
        path = fh.name
    yield path
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@pytest_asyncio.fixture()
async def test_client(
    valid_meter_config_file: str,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test AsyncClient backed by an in-memory SQLite database.

    Patches:
    - DATABASE_URL → SQLite in-memory
    - KWH_METER_CONFIG → temp config file with valid meter data
    - app.database engine/session → SQLite engine so create_all works
    """
    monkeypatch.setenv("KWH_METER_CONFIG", valid_meter_config_file)
    monkeypatch.setenv("DATABASE_URL", TEST_DB_URL)

    # Patch the database module BEFORE importing main so the engine uses SQLite
    import app.database as db_module

    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(db_module, "AsyncSessionLocal", test_session_factory)

    # Stub the notification job so scheduled fires can never issue real
    # outbound HTTP requests from the test suite.
    import app.notifications as notifications_module

    async def _no_send(zaehler_nr: str) -> None:
        return None

    monkeypatch.setattr(notifications_module, "send_reading_reminder", _no_send)

    # Now import and build the app
    from app.main import app as fastapi_app

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        # Manually trigger lifespan since httpx doesn't do it by default
        # Use the lifespan context manager
        async with fastapi_app.router.lifespan_context(fastapi_app):
            yield client

    await test_engine.dispose()
