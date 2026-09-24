"""Analytics router — GET /api/analytics/intervals."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Reading
from ..schemas import IntervalOut

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/intervals", response_model=list[IntervalOut])
async def get_intervals(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> list[IntervalOut]:
    """Return per-interval metrics between consecutive readings, oldest first.

    Each interval spans two consecutive readings of the active meter and
    reports the consumed energy (ΔkWh), the elapsed duration, and the derived
    average power (kW). Average power is ``None`` when the two readings share
    the same timestamp.
    """
    zaehler_nr: str = request.app.state.active_zaehler_nr

    result = await session.execute(
        select(Reading)
        .where(Reading.zaehler_nr == zaehler_nr)
        .order_by(Reading.timestamp.asc())
    )
    readings = list(result.scalars().all())

    intervals: list[IntervalOut] = []
    for prev, curr in zip(readings, readings[1:]):
        energy = float(curr.value_kwh) - float(prev.value_kwh)
        duration_hours = (curr.timestamp - prev.timestamp).total_seconds() / 3600
        avg_kw = energy / duration_hours if duration_hours > 0 else None
        intervals.append(
            IntervalOut(
                start=prev.timestamp.isoformat(),
                end=curr.timestamp.isoformat(),
                energy_kwh=energy,
                duration_hours=duration_hours,
                avg_power_kw=avg_kw,
            )
        )
    return intervals
