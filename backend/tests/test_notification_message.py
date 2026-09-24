"""
Unit tests for the reminder message builder (feature 0012, decision 7):
  heute / gestern / am DD.MM.YYYY abstraction and the no-reading fallback.
"""

from __future__ import annotations

import datetime

from app.notifications import BASE_MESSAGE, build_reminder_message


def test_message_with_reading_today() -> None:
    """A reading from earlier today must produce the 'heute' reference."""
    now = datetime.datetime(2026, 9, 24, 20, 0)
    last = datetime.datetime(2026, 9, 24, 16, 0)
    assert (
        build_reminder_message(last, now)
        == f"{BASE_MESSAGE} Die letzte war heute um 16:00"
    )


def test_message_with_reading_yesterday() -> None:
    """A reading from yesterday must produce the 'gestern' reference."""
    now = datetime.datetime(2026, 9, 24, 8, 0)
    last = datetime.datetime(2026, 9, 23, 16, 0)
    assert (
        build_reminder_message(last, now)
        == f"{BASE_MESSAGE} Die letzte war gestern um 16:00"
    )


def test_message_with_older_reading() -> None:
    """An older reading must produce the absolute 'am DD.MM.YYYY' reference."""
    now = datetime.datetime(2026, 9, 24, 8, 0)
    last = datetime.datetime(2026, 9, 20, 16, 5)
    assert (
        build_reminder_message(last, now)
        == f"{BASE_MESSAGE} Die letzte war am 20.09.2026 um 16:05"
    )


def test_message_across_month_boundary() -> None:
    """A reading on the last day of the previous month must be 'gestern'."""
    now = datetime.datetime(2026, 3, 1, 7, 0)
    last = datetime.datetime(2026, 2, 28, 22, 30)
    assert (
        build_reminder_message(last, now)
        == f"{BASE_MESSAGE} Die letzte war gestern um 22:30"
    )


def test_message_across_year_boundary() -> None:
    """A reading on 31.12. must be 'gestern' on 01.01. of the next year."""
    now = datetime.datetime(2027, 1, 1, 7, 0)
    last = datetime.datetime(2026, 12, 31, 23, 0)
    assert (
        build_reminder_message(last, now)
        == f"{BASE_MESSAGE} Die letzte war gestern um 23:00"
    )


def test_message_without_any_reading() -> None:
    """Without readings the fallback text must be used."""
    now = datetime.datetime(2026, 9, 24, 8, 0)
    assert (
        build_reminder_message(None, now)
        == f"{BASE_MESSAGE} Noch keine Ablesung erfasst."
    )


def test_message_with_timezone_aware_timestamps() -> None:
    """Timezone-aware inputs are converted to local time before comparing."""
    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime(2026, 9, 24, 20, 0, tzinfo=local_tz)
    last = datetime.datetime(2026, 9, 24, 16, 0, tzinfo=local_tz)
    assert (
        build_reminder_message(last, now)
        == f"{BASE_MESSAGE} Die letzte war heute um 16:00"
    )
