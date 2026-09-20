"""Pydantic schemas for the kwh-meter API."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, field_validator, model_validator


class ReadingCreate(BaseModel):
    """Input schema for creating a new reading."""

    timestamp: datetime
    value_kwh: Decimal
    comment: str | None = None

    @field_validator("value_kwh", mode="before")
    @classmethod
    def round_and_validate_value(cls, v: object) -> Decimal:
        d = Decimal(str(v))
        if d <= 0:
            raise ValueError("value_kwh must be a positive number")
        # Round to exactly 1 decimal place
        return d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    @field_validator("comment", mode="before")
    @classmethod
    def sanitise_comment(cls, v: object) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        # Replace one or more consecutive tab characters with a single space
        s = re.sub(r"\t+", " ", s)
        # Cap at 255 characters
        return s[:255]


class ReadingOut(BaseModel):
    """Output schema for a single reading."""

    id: int
    zaehler_nr: str
    timestamp: str          # ISO 8601 string
    value_kwh: float        # always 1 decimal place
    comment: str | None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def coerce_fields(cls, data: object) -> object:
        """Convert ORM model fields to the expected output types."""
        if hasattr(data, "__dict__") or hasattr(data, "__table__"):
            # ORM object — convert to dict-like
            return {
                "id": data.id,
                "zaehler_nr": data.zaehler_nr,
                "timestamp": data.timestamp.isoformat(),
                "value_kwh": float(data.value_kwh),
                "comment": data.comment,
            }
        return data


class ReadingsPage(BaseModel):
    """Paginated list of readings."""

    items: list[ReadingOut]
    page: int
    page_size: int
    total: int
