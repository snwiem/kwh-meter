"""
Tests for scheduler job management and ntfy publishing (feature 0012).

Covers:
- reschedule_notification_times(): job ids/counts after create and delete,
  zero jobs for an empty plan (acceptance criteria "plan changes without
  restart" and "empty plan = no notifications")
- send_reading_reminder(): POST to {NTFY_URL}/{topic} with the message body,
  and that connection/non-2xx errors are swallowed (never crash the scheduler)

Note: the real send_reading_reminder is imported at module level on purpose —
the conftest fixture replaces the module attribute with a no-op stub so
scheduled jobs can never issue real HTTP from the suite; the directly imported
function object is the unstubbed original. httpx.AsyncClient is monkeypatched
with a fake in every publishing test, so no outbound traffic happens here.
"""

from __future__ import annotations

import datetime

import httpx
import pytest
from httpx import AsyncClient

import app.notifications as notifications
from app.notifications import BASE_MESSAGE, send_reading_reminder
from tests.conftest import VALID_METER_DATA


@pytest.mark.asyncio
async def test_scheduler_jobs_follow_plan_changes(test_client: AsyncClient) -> None:
    """Jobs must appear after create, disappear after delete; empty plan = zero jobs."""
    scheduler = notifications._scheduler
    assert scheduler is not None, "lifespan must have started the scheduler"

    # Empty plan → no jobs
    assert scheduler.get_jobs() == []

    first = await test_client.post("/api/notification-times", json={"time": "08:00"})
    second = await test_client.post("/api/notification-times", json={"time": "20:00"})
    assert first.status_code == 201 and second.status_code == 201
    first_id = first.json()["id"]
    second_id = second.json()["id"]

    assert sorted(job.id for job in scheduler.get_jobs()) == sorted(
        [f"notification-time-{first_id}", f"notification-time-{second_id}"]
    )

    response = await test_client.delete(f"/api/notification-times/{first_id}")
    assert response.status_code == 204
    assert [job.id for job in scheduler.get_jobs()] == [f"notification-time-{second_id}"]

    response = await test_client.delete(f"/api/notification-times/{second_id}")
    assert response.status_code == 204
    assert scheduler.get_jobs() == []


class _FakeResponse:
    def __init__(self, status_code: int, url: str) -> None:
        self.status_code = status_code
        self._url = url

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", self._url)
            raise httpx.HTTPStatusError(
                f"error {self.status_code}",
                request=request,
                response=httpx.Response(self.status_code, request=request),
            )


def _install_fake_httpx(
    monkeypatch: pytest.MonkeyPatch, captured: list, behavior: str = "ok"
) -> None:
    """Replace httpx.AsyncClient with a fake that records posts or fails."""

    class _FakeAsyncClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> "_FakeAsyncClient":
            return self

        async def __aexit__(self, *exc_info: object) -> bool:
            return False

        async def post(self, url: str, content: bytes | None = None) -> _FakeResponse:
            captured.append({"url": url, "content": content})
            if behavior == "connect-error":
                raise httpx.ConnectError("connection refused")
            status_code = 500 if behavior == "http-error" else 200
            response = _FakeResponse(status_code, url)
            response.raise_for_status()
            return response

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)


@pytest.mark.asyncio
async def test_send_reading_reminder_posts_message(
    test_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The job must POST the reminder message to {NTFY_URL}/{topic}."""
    monkeypatch.setenv("NTFY_URL", "http://ntfy-test:80/")  # trailing slash on purpose
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    captured: list = []
    _install_fake_httpx(monkeypatch, captured)

    # Record a reading so the message references it
    created = await test_client.post(
        "/api/readings",
        json={
            "timestamp": datetime.datetime.now().isoformat(),
            "value_kwh": 1234.5,
        },
    )
    assert created.status_code == 201

    await send_reading_reminder(VALID_METER_DATA["zaehler_nr"])

    assert len(captured) == 1
    assert captured[0]["url"] == "http://ntfy-test:80/test-topic"
    body = captured[0]["content"].decode("utf-8")
    assert body.startswith(BASE_MESSAGE)
    assert "Die letzte war" in body


@pytest.mark.asyncio
async def test_send_reading_reminder_without_readings(
    test_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no readings the fallback message must be published."""
    monkeypatch.setenv("NTFY_URL", "http://ntfy-test:80")
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    captured: list = []
    _install_fake_httpx(monkeypatch, captured)

    await send_reading_reminder(VALID_METER_DATA["zaehler_nr"])

    assert len(captured) == 1
    assert captured[0]["url"] == "http://ntfy-test:80/test-topic"
    assert (
        captured[0]["content"].decode("utf-8")
        == f"{BASE_MESSAGE} Noch keine Ablesung erfasst."
    )


@pytest.mark.asyncio
async def test_send_reading_reminder_swallows_connection_error(
    test_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A connection error must be logged and swallowed, never propagate."""
    monkeypatch.setenv("NTFY_URL", "http://ntfy-test:80")
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    captured: list = []
    _install_fake_httpx(monkeypatch, captured, behavior="connect-error")

    await send_reading_reminder(VALID_METER_DATA["zaehler_nr"])  # must not raise

    assert len(captured) == 1


@pytest.mark.asyncio
async def test_send_reading_reminder_swallows_http_error(
    test_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-2xx response must be logged and swallowed, never propagate."""
    monkeypatch.setenv("NTFY_URL", "http://ntfy-test:80")
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    captured: list = []
    _install_fake_httpx(monkeypatch, captured, behavior="http-error")

    await send_reading_reminder(VALID_METER_DATA["zaehler_nr"])  # must not raise

    assert len(captured) == 1
