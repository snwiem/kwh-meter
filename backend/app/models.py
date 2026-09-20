"""SQLAlchemy ORM models for kwh-meter."""

from __future__ import annotations

from sqlalchemy import String
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
