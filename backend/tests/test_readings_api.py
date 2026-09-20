"""Tests for POST /api/readings and GET /api/readings."""

from __future__ import annotations

import datetime

import pytest
from httpx import AsyncClient


VALID_PAYLOAD = {
    "timestamp": "2024-06-01T10:00:00+00:00",
    "value_kwh": 1234.5,
    "comment": None,
}


@pytest.mark.asyncio
async def test_create_reading_happy_path(test_client: AsyncClient) -> None:
    response = await test_client.post("/api/readings", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["zaehler_nr"] == "DE00012345678901234567890"
    assert data["value_kwh"] == 1234.5
    assert data["comment"] is None
    assert "id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_create_reading_integer_value_gets_decimal(test_client: AsyncClient) -> None:
    """Integer value 1234 should be stored and returned as 1234.0."""
    payload = {**VALID_PAYLOAD, "value_kwh": 1234}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 201
    assert response.json()["value_kwh"] == 1234.0


@pytest.mark.asyncio
async def test_create_reading_rounds_to_one_decimal(test_client: AsyncClient) -> None:
    """1234.56 should be rounded to 1234.6."""
    payload = {**VALID_PAYLOAD, "value_kwh": 1234.56}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 201
    assert response.json()["value_kwh"] == 1234.6


@pytest.mark.asyncio
async def test_create_reading_negative_value_rejected(test_client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "value_kwh": -1.0}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_reading_zero_value_rejected(test_client: AsyncClient) -> None:
    payload = {**VALID_PAYLOAD, "value_kwh": 0}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_reading_comment_tabs_replaced(test_client: AsyncClient) -> None:
    """Tab characters in comments must be replaced with spaces."""
    payload = {**VALID_PAYLOAD, "comment": "hello\t\tworld"}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 201
    assert response.json()["comment"] == "hello world"


@pytest.mark.asyncio
async def test_list_readings_sorted_newest_first(test_client: AsyncClient) -> None:
    """GET /api/readings returns readings sorted by timestamp descending."""
    # Insert two readings with different timestamps
    older = {**VALID_PAYLOAD, "timestamp": "2024-01-01T08:00:00+00:00", "value_kwh": 100.0}
    newer = {**VALID_PAYLOAD, "timestamp": "2024-06-01T12:00:00+00:00", "value_kwh": 200.0}
    await test_client.post("/api/readings", json=older)
    await test_client.post("/api/readings", json=newer)

    response = await test_client.get("/api/readings")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    # Newest first
    assert data["items"][0]["value_kwh"] == 200.0
    assert data["items"][1]["value_kwh"] == 100.0


@pytest.mark.asyncio
async def test_create_reading_below_previous_rejected(test_client: AsyncClient) -> None:
    """A value lower than the previous reading's value must be rejected."""
    await test_client.post("/api/readings", json={**VALID_PAYLOAD, "timestamp": "2024-01-01T08:00:00+00:00", "value_kwh": 1000.0})
    payload = {**VALID_PAYLOAD, "timestamp": "2024-06-01T10:00:00+00:00", "value_kwh": 999.0}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_reading_above_next_rejected(test_client: AsyncClient) -> None:
    """A value higher than the following reading's value must be rejected."""
    await test_client.post("/api/readings", json={**VALID_PAYLOAD, "timestamp": "2024-12-01T10:00:00+00:00", "value_kwh": 2000.0})
    payload = {**VALID_PAYLOAD, "timestamp": "2024-06-01T10:00:00+00:00", "value_kwh": 2500.0}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_reading_equal_to_previous_allowed(test_client: AsyncClient) -> None:
    """A value equal to the previous reading is valid (meter didn't change)."""
    await test_client.post("/api/readings", json={**VALID_PAYLOAD, "timestamp": "2024-01-01T08:00:00+00:00", "value_kwh": 1000.0})
    payload = {**VALID_PAYLOAD, "timestamp": "2024-06-01T10:00:00+00:00", "value_kwh": 1000.0}
    response = await test_client.post("/api/readings", json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_neighbours_returns_correct_readings(test_client: AsyncClient) -> None:
    """GET /api/readings/neighbours returns the readings directly before and after the timestamp."""
    await test_client.post("/api/readings", json={**VALID_PAYLOAD, "timestamp": "2024-01-01T08:00:00+00:00", "value_kwh": 100.0})
    await test_client.post("/api/readings", json={**VALID_PAYLOAD, "timestamp": "2024-12-01T08:00:00+00:00", "value_kwh": 500.0})

    response = await test_client.get("/api/readings/neighbours?timestamp=2024-06-01T10:00:00%2B00:00")
    assert response.status_code == 200
    data = response.json()
    assert data["previous"]["value_kwh"] == 100.0
    assert data["next"]["value_kwh"] == 500.0


@pytest.mark.asyncio
async def test_get_neighbours_no_neighbours(test_client: AsyncClient) -> None:
    """Returns null for both when no readings exist."""
    response = await test_client.get("/api/readings/neighbours?timestamp=2024-06-01T10:00:00%2B00:00")
    assert response.status_code == 200
    data = response.json()
    assert data["previous"] is None
    assert data["next"] is None


@pytest.mark.asyncio
async def test_list_readings_pagination(test_client: AsyncClient) -> None:
    """Page 2 returns the correct items when there are more than page_size readings."""
    # Insert 12 readings
    for i in range(12):
        ts = f"2024-01-{i + 1:02d}T10:00:00+00:00"
        await test_client.post("/api/readings", json={**VALID_PAYLOAD, "timestamp": ts, "value_kwh": float(i + 1)})

    # Page 1 — 10 items (newest first = day 12 down to day 3)
    r1 = await test_client.get("/api/readings?page=1&page_size=10")
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["total"] == 12
    assert len(d1["items"]) == 10

    # Page 2 — 2 remaining items
    r2 = await test_client.get("/api/readings?page=2&page_size=10")
    assert r2.status_code == 200
    d2 = r2.json()
    assert len(d2["items"]) == 2
    assert d2["page"] == 2
