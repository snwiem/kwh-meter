"""Readings router — POST /api/readings and GET /api/readings."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Reading
from ..schemas import ReadingCreate, ReadingOut, ReadingsPage

router = APIRouter(prefix="/api/readings", tags=["readings"])


@router.post("", response_model=ReadingOut, status_code=status.HTTP_201_CREATED)
async def create_reading(
    body: ReadingCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ReadingOut:
    """Record a new kWh reading for the currently active meter."""
    zaehler_nr: str = request.app.state.active_zaehler_nr
    reading = Reading(
        zaehler_nr=zaehler_nr,
        timestamp=body.timestamp,
        value_kwh=body.value_kwh,
        comment=body.comment,
    )
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return ReadingOut.model_validate(reading)


@router.get("", response_model=ReadingsPage)
async def list_readings(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_session),
) -> ReadingsPage:
    """Return a paginated list of readings for the active meter, newest first."""
    zaehler_nr: str = request.app.state.active_zaehler_nr

    # Clamp page_size to max 10
    page_size = min(page_size, 10)
    page = max(page, 1)
    offset = (page - 1) * page_size

    # Total count
    count_result = await session.execute(
        select(func.count(Reading.id)).where(Reading.zaehler_nr == zaehler_nr)
    )
    total: int = count_result.scalar_one()

    # Paginated rows
    rows_result = await session.execute(
        select(Reading)
        .where(Reading.zaehler_nr == zaehler_nr)
        .order_by(Reading.timestamp.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = rows_result.scalars().all()

    return ReadingsPage(
        items=[ReadingOut.model_validate(r) for r in rows],
        page=page,
        page_size=page_size,
        total=total,
    )
