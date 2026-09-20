"""Readings router — POST /api/readings and GET /api/readings."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Reading
from ..schemas import ReadingCreate, ReadingNeighbours, ReadingOut, ReadingsPage

router = APIRouter(prefix="/api/readings", tags=["readings"])


@router.get("/neighbours", response_model=ReadingNeighbours)
async def get_neighbours(
    timestamp: datetime,
    request: Request,
    exclude_id: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> ReadingNeighbours:
    """Return the nearest reading before and after the given timestamp."""
    zaehler_nr: str = request.app.state.active_zaehler_nr
    return await _fetch_neighbours(session, zaehler_nr, timestamp, exclude_id)


async def _fetch_neighbours(
    session: AsyncSession,
    zaehler_nr: str,
    timestamp: datetime,
    exclude_id: int | None = None,
) -> ReadingNeighbours:
    """Fetch the immediately preceding and following readings for a timestamp.

    When ``exclude_id`` is provided, that reading is left out of the result so
    it is not treated as its own neighbour.
    """
    prev_conditions = [Reading.zaehler_nr == zaehler_nr, Reading.timestamp < timestamp]
    if exclude_id is not None:
        prev_conditions.append(Reading.id != exclude_id)
    prev_result = await session.execute(
        select(Reading)
        .where(*prev_conditions)
        .order_by(Reading.timestamp.desc())
        .limit(1)
    )
    prev = prev_result.scalar_one_or_none()

    next_conditions = [Reading.zaehler_nr == zaehler_nr, Reading.timestamp > timestamp]
    if exclude_id is not None:
        next_conditions.append(Reading.id != exclude_id)
    next_result = await session.execute(
        select(Reading)
        .where(*next_conditions)
        .order_by(Reading.timestamp.asc())
        .limit(1)
    )
    nxt = next_result.scalar_one_or_none()

    return ReadingNeighbours(
        previous=ReadingOut.model_validate(prev) if prev else None,
        next=ReadingOut.model_validate(nxt) if nxt else None,
    )


@router.post("", response_model=ReadingOut, status_code=status.HTTP_201_CREATED)
async def create_reading(
    body: ReadingCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ReadingOut:
    """Record a new kWh reading for the currently active meter."""
    zaehler_nr: str = request.app.state.active_zaehler_nr

    # Validate value fits between neighbouring readings
    neighbours = await _fetch_neighbours(session, zaehler_nr, body.timestamp)
    if neighbours.previous is not None and body.value_kwh < Decimal(
        str(neighbours.previous.value_kwh)
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Wert muss mindestens {neighbours.previous.value_kwh} kWh betragen "
                f"(vorherige Ablesung)."
            ),
        )
    if neighbours.next is not None and body.value_kwh > Decimal(
        str(neighbours.next.value_kwh)
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Wert darf höchstens {neighbours.next.value_kwh} kWh betragen "
                f"(nächste Ablesung)."
            ),
        )

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


@router.get("/{id}", response_model=ReadingOut)
async def get_reading(
    id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ReadingOut:
    """Return a single reading by its ID, if it belongs to the active meter."""
    zaehler_nr: str = request.app.state.active_zaehler_nr
    
    result = await session.execute(
        select(Reading)
        .where(Reading.id == id, Reading.zaehler_nr == zaehler_nr)
    )
    reading = result.scalar_one_or_none()
    
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    return ReadingOut.model_validate(reading)


@router.put("/{id}", response_model=ReadingOut)
async def update_reading(
    id: int,
    body: ReadingCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ReadingOut:
    """Update an existing reading by its ID."""
    zaehler_nr: str = request.app.state.active_zaehler_nr

    result = await session.execute(
        select(Reading)
        .where(Reading.id == id, Reading.zaehler_nr == zaehler_nr)
    )
    reading = result.scalar_one_or_none()

    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    # Validate value fits between neighbouring readings, excluding the reading itself
    neighbours = await _fetch_neighbours(
        session, zaehler_nr, body.timestamp, exclude_id=id
    )
    if neighbours.previous is not None and body.value_kwh < Decimal(
        str(neighbours.previous.value_kwh)
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Wert muss mindestens {neighbours.previous.value_kwh} kWh betragen "
                f"(vorherige Ablesung)."
            ),
        )
    if neighbours.next is not None and body.value_kwh > Decimal(
        str(neighbours.next.value_kwh)
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Wert darf höchstens {neighbours.next.value_kwh} kWh betragen "
                f"(nächste Ablesung)."
            ),
        )

    reading.timestamp = body.timestamp
    reading.value_kwh = body.value_kwh
    reading.comment = body.comment

    await session.commit()
    await session.refresh(reading)
    return ReadingOut.model_validate(reading)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reading(
    id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a reading by its ID, if it belongs to the active meter."""
    zaehler_nr: str = request.app.state.active_zaehler_nr

    result = await session.execute(
        select(Reading)
        .where(Reading.id == id, Reading.zaehler_nr == zaehler_nr)
    )
    reading = result.scalar_one_or_none()

    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    await session.delete(reading)
    await session.commit()
