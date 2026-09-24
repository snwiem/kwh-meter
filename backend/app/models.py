"""SQLAlchemy ORM models for kwh-meter."""

from __future__ import annotations

import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Meter(Base):
    """
    Represents the energy meter configured via the JSON config file.

    zaehler_nr is the primary key (the German meter ID).
    One row per distinct zaehler_nr is kept; a config change that introduces
    a new zaehler_nr simply creates a new row — old rows are never deleted.
    """

    __tablename__ = "meters"

    zaehler_nr: Mapped[str] = mapped_column(String, primary_key=True)
    street: Mapped[str] = mapped_column(String, nullable=False)
    house_number: Mapped[str] = mapped_column(String, nullable=False)
    postal_code: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Meter zaehler_nr={self.zaehler_nr!r} "
            f"city={self.city!r}>"
        )


class Reading(Base):
    """
    A single kWh meter reading recorded by the user.

    Always associated with the currently active zaehler_nr.
    Timestamp is stored as UTC-aware datetime.
    """

    __tablename__ = "readings"
    __table_args__ = (Index("ix_readings_zaehler_nr_timestamp", "zaehler_nr", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    zaehler_nr: Mapped[str] = mapped_column(
        String, ForeignKey("meters.zaehler_nr"), nullable=False
    )
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    value_kwh: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Reading id={self.id!r} zaehler_nr={self.zaehler_nr!r} "
            f"timestamp={self.timestamp!r} value_kwh={self.value_kwh!r}>"
        )


class NotificationTime(Base):
    """
    One entry of the notification plan: a daily time (HH:MM, server local
    timezone) at which a reading-reminder notification is sent via ntfy.
    Fires every day regardless of weekday; the time is unique.
    """

    __tablename__ = "notification_times"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    time: Mapped[datetime.time] = mapped_column(Time, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<NotificationTime id={self.id!r} time={self.time!r}>"
