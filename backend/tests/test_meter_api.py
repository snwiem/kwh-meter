"""
Tests for GET /api/meter endpoint.

Uses the test_client fixture from conftest.py which sets up an in-memory
SQLite database and a valid meter config file.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import VALID_METER_DATA


@pytest.mark.asyncio
async def test_get_meter_returns_correct_data(test_client: AsyncClient) -> None:
    """GET /api/meter must return the meter data from the config file."""
    response = await test_client.get("/api/meter")
    assert response.status_code == 200
    body = response.json()
    assert body["zaehler_nr"] == VALID_METER_DATA["zaehler_nr"]
    assert body["street"] == VALID_METER_DATA["street"]
    assert body["house_number"] == VALID_METER_DATA["house_number"]
    assert body["postal_code"] == VALID_METER_DATA["postal_code"]
    assert body["city"] == VALID_METER_DATA["city"]


@pytest.mark.asyncio
async def test_health_endpoint(test_client: AsyncClient) -> None:
    """GET /health must return 200 OK."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
