"""
Notification scheduling and ntfy publishing for reading reminders.

The notification plan is a list of daily times (NotificationTime rows) stored
in the database. An APScheduler AsyncIOScheduler runs one cron job per time
(server local timezone). On fire, the job builds a reminder message that
references the latest reading of the active meter and publishes it to the
self-hosted ntfy server via a plain HTTP POST (no auth, LAN deployment).

Sending is unconditional (feature 0012, decision 4); a send failure is logged
and must never crash the scheduler. Plan changes are applied without a
restart: the CRUD router calls reschedule_notification_times() after every
successful create/delete (decision 8).
"""

from __future__ import annotations

import datetime
import logging

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from . import database as db_module
from .config import load_ntfy_settings
from .models import NotificationTime, Reading

logger = logging.getLogger(__name__)

BASE_MESSAGE = "⏰ Zeit für eine Zählerablesung!"
NO_READING_MESSAGE = "Noch keine Ablesung erfasst."

# Module state managed by start_scheduler()/shutdown_scheduler() (lifespan).
_scheduler: AsyncIOScheduler | None = None
_active_zaehler_nr: str | None = None


def build_reminder_message(
    last_timestamp: datetime.datetime | None,
    now: datetime.datetime,
) -> str:
    """
    Build the reminder message text (pure function, unit-testable).

    ``last_timestamp`` is the timestamp of the latest reading (or None when no
    reading exists); ``now`` is the current time. Both may be naive (interpreted
    as local time) or timezone-aware (converted to local time). The reference
    uses the German relative-date abstraction heute / gestern / am DD.MM.YYYY.
    """
    if last_timestamp is None:
        return f"{BASE_MESSAGE} {NO_READING_MESSAGE}"

    ref_now = now.astimezone() if now.tzinfo is not None else now
    ref_ts = (
        last_timestamp.astimezone()
        if last_timestamp.tzinfo is not None
        else last_timestamp
    )

    if ref_ts.date() == ref_now.date():
        return f"{BASE_MESSAGE} Die letzte war heute um {ref_ts:%H:%M}"
    if ref_ts.date() == (ref_now - datetime.timedelta(days=1)).date():
        return f"{BASE_MESSAGE} Die letzte war gestern um {ref_ts:%H:%M}"
    return f"{BASE_MESSAGE} Die letzte war am {ref_ts:%d.%m.%Y} um {ref_ts:%H:%M}"


async def send_reading_reminder(zaehler_nr: str) -> None:
    """
    Scheduler job: query the latest reading for the active meter, build the
    reminder message and publish it to the ntfy topic. Failures are logged
    and swallowed so the scheduler keeps running.
    """
    ntfy = load_ntfy_settings()
    try:
        # Read db_module at call time so tests can patch the session factory
        async with db_module.AsyncSessionLocal() as session:
            result = await session.execute(
                select(Reading.timestamp)
                .where(Reading.zaehler_nr == zaehler_nr)
                .order_by(Reading.timestamp.desc())
                .limit(1)
            )
            last_timestamp = result.scalar_one_or_none()

        message = build_reminder_message(last_timestamp, datetime.datetime.now())
        url = f"{ntfy.ntfy_url.rstrip('/')}/{ntfy.ntfy_topic}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, content=message.encode("utf-8"))
            response.raise_for_status()
        logger.info("Reading reminder published to ntfy topic %r", ntfy.ntfy_topic)
    except Exception:
        logger.exception("Failed to send reading reminder notification")


def start_scheduler(zaehler_nr: str) -> None:
    """Create and start the scheduler (called from the FastAPI lifespan)."""
    global _scheduler, _active_zaehler_nr
    _active_zaehler_nr = zaehler_nr
    shutdown_scheduler()
    _scheduler = AsyncIOScheduler()  # default timezone: server local time
    _scheduler.start()


def shutdown_scheduler() -> None:
    """Stop the scheduler if it is running (called on app shutdown)."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)


async def reschedule_notification_times() -> None:
    """
    Rebuild all daily jobs from the NotificationTime rows in the database.
    Called on startup and after every successful plan change so edits take
    effect without a restart. An empty plan removes all jobs (decision 9).
    """
    if _scheduler is None or _active_zaehler_nr is None:
        return

    for job in _scheduler.get_jobs():
        job.remove()

    async with db_module.AsyncSessionLocal() as session:
        result = await session.execute(
            select(NotificationTime).order_by(NotificationTime.time)
        )
        rows = result.scalars().all()

    for row in rows:
        _scheduler.add_job(
            send_reading_reminder,
            CronTrigger(hour=row.time.hour, minute=row.time.minute),
            args=[_active_zaehler_nr],
            id=f"notification-time-{row.id}",
            replace_existing=True,
        )
    logger.info("Notification plan loaded: %d daily job(s)", len(rows))
