"""Router for meter-related endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Meter

router = APIRouter(prefix="/api/meter", tags=["meter"])


class MeterResponse(BaseModel):
    """Response schema for the active meter."""

    zaehler_nr: str
    street: str
    house_number: str
    postal_code: str
    city: str

    model_config = {"from_attributes": True}


@router.get("", response_model=MeterResponse)
async def get_meter(session: AsyncSession = Depends(get_session)) -> MeterResponse:
    """
    Return the currently active energy meter (the one matching the
    zaehler_nr from the config file that was seeded on startup).
    The active zaehler_nr is stored in the app state set during startup.
    """
    from ..main import app as current_app  # avoid circular import at module level

    active_zaehler_nr: str = current_app.state.active_zaehler_nr
    result = await session.execute(
        select(Meter).where(Meter.zaehler_nr == active_zaehler_nr)
    )
    meter = result.scalar_one_or_none()
    if meter is None:
        raise HTTPException(status_code=404, detail="Active meter not found in database")
    return MeterResponse.model_validate(meter)
