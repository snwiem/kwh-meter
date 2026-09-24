"""Tests for GET /api/analytics/intervals."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


def _reading(timestamp: str, value: float) -> dict:
    return {"timestamp": timestamp, "value_kwh": value, "comment": None}


@pytest.mark.asyncio
async def test_intervals_empty_when_no_readings(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/analytics/intervals")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_intervals_empty_with_single_reading(test_client: AsyncClient) -> None:
    await test_client.post("/api/readings", json=_reading("2024-06-01T10:00:00", 100.0))
    response = await test_client.get("/api/analytics/intervals")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_intervals_computed_between_consecutive_readings(
    test_client: AsyncClient,
) -> None:
    # Three readings → two intervals, oldest first
    await test_client.post("/api/readings", json=_reading("2024-06-01T10:00:00", 100.0))
    await test_client.post("/api/readings", json=_reading("2024-06-01T22:00:00", 103.6))
    await test_client.post("/api/readings", json=_reading("2024-06-02T22:00:00", 108.4))

    response = await test_client.get("/api/analytics/intervals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    first, second = data

    # Interval 1: 3.6 kWh over 12 h → 0.3 kW
    assert first["start"] == "2024-06-01T10:00:00"
    assert first["end"] == "2024-06-01T22:00:00"
    assert first["energy_kwh"] == pytest.approx(3.6)
    assert first["duration_hours"] == pytest.approx(12.0)
    assert first["avg_power_kw"] == pytest.approx(0.3)

    # Interval 2: 4.8 kWh over 24 h → 0.2 kW
    assert second["start"] == "2024-06-01T22:00:00"
    assert second["end"] == "2024-06-02T22:00:00"
    assert second["energy_kwh"] == pytest.approx(4.8)
    assert second["duration_hours"] == pytest.approx(24.0)
    assert second["avg_power_kw"] == pytest.approx(0.2)


@pytest.mark.asyncio
async def test_intervals_zero_duration_yields_null_avg_power(
    test_client: AsyncClient,
) -> None:
    """Two readings with identical timestamps → duration 0 → avg_power_kw is null."""
    await test_client.post("/api/readings", json=_reading("2024-06-01T10:00:00", 100.0))
    await test_client.post("/api/readings", json=_reading("2024-06-01T10:00:00", 105.0))

    response = await test_client.get("/api/analytics/intervals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["duration_hours"] == 0
    assert data[0]["energy_kwh"] == pytest.approx(5.0)
    assert data[0]["avg_power_kw"] is None
