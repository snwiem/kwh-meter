"""
Tests for the notification plan API (feature 0012):
  GET/POST /api/notification-times, DELETE /api/notification-times/{id},
  GET /api/notifications/connection-info.

Uses the test_client fixture from conftest.py (in-memory SQLite + valid meter
config). The notification scheduler runs inside the test lifespan but has no
jobs to fire, so it is inert here.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_notification_times_initially_empty(test_client: AsyncClient) -> None:
    """GET /api/notification-times must return an empty list initially."""
    response = await test_client.get("/api/notification-times")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_notification_time(test_client: AsyncClient) -> None:
    """POST /api/notification-times must create a time and return 201."""
    response = await test_client.post("/api/notification-times", json={"time": "08:00"})
    assert response.status_code == 201
    body = response.json()
    assert body["time"] == "08:00"
    assert isinstance(body["id"], int)


@pytest.mark.asyncio
async def test_list_sorted_ascending(test_client: AsyncClient) -> None:
    """GET must return all times sorted ascending, regardless of insert order."""
    for time_value in ["20:00", "08:00", "12:30"]:
        response = await test_client.post(
            "/api/notification-times", json={"time": time_value}
        )
        assert response.status_code == 201

    response = await test_client.get("/api/notification-times")
    assert response.status_code == 200
    assert [item["time"] for item in response.json()] == ["08:00", "12:30", "20:00"]


@pytest.mark.asyncio
async def test_create_invalid_format_rejected(test_client: AsyncClient) -> None:
    """POST with an invalid HH:MM value must return 422."""
    for invalid in ["25:00", "12:60", "8:00", "abc", ""]:
        response = await test_client.post(
            "/api/notification-times", json={"time": invalid}
        )
        assert response.status_code == 422, f"expected 422 for {invalid!r}"


@pytest.mark.asyncio
async def test_create_duplicate_rejected(test_client: AsyncClient) -> None:
    """POST with an already existing time must return 409."""
    first = await test_client.post("/api/notification-times", json={"time": "08:00"})
    assert first.status_code == 201

    duplicate = await test_client.post("/api/notification-times", json={"time": "08:00"})
    assert duplicate.status_code == 409


@pytest.mark.asyncio
async def test_delete_notification_time(test_client: AsyncClient) -> None:
    """DELETE must remove the time and return 204; the list must shrink."""
    created = await test_client.post("/api/notification-times", json={"time": "08:00"})
    time_id = created.json()["id"]

    response = await test_client.delete(f"/api/notification-times/{time_id}")
    assert response.status_code == 204

    listing = await test_client.get("/api/notification-times")
    assert listing.json() == []


@pytest.mark.asyncio
async def test_delete_missing_returns_404(test_client: AsyncClient) -> None:
    """DELETE of a non-existent id must return 404."""
    response = await test_client.delete("/api/notification-times/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_connection_info_defaults(test_client: AsyncClient) -> None:
    """GET connection-info must return the ntfy defaults when env vars are unset."""
    response = await test_client.get("/api/notifications/connection-info")
    assert response.status_code == 200
    assert response.json() == {
        "public_url": "http://localhost:8080",
        "topic": "kwh-meter-readings",
    }


@pytest.mark.asyncio
async def test_connection_info_reflects_env(
    test_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GET connection-info must reflect NTFY_PUBLIC_URL / NTFY_TOPIC overrides."""
    monkeypatch.setenv("NTFY_PUBLIC_URL", "http://192.168.1.10:8080")
    monkeypatch.setenv("NTFY_TOPIC", "custom-topic")

    response = await test_client.get("/api/notifications/connection-info")
    assert response.status_code == 200
    assert response.json() == {
        "public_url": "http://192.168.1.10:8080",
        "topic": "custom-topic",
    }
