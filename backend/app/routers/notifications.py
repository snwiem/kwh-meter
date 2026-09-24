"""Router for the notification plan (feature 0012).

CRUD for daily notification times plus the ntfy connection info shown in the
frontend. After every successful create/delete the scheduler jobs are rebuilt
so plan changes take effect without a restart.
"""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import notifications
from ..config import load_ntfy_settings
from ..database import get_session
from ..models import NotificationTime
from ..schemas import ConnectionInfoOut, NotificationTimeCreate, NotificationTimeOut

router = APIRouter(prefix="/api", tags=["notifications"])


def _to_out(row: NotificationTime) -> NotificationTimeOut:
    return NotificationTimeOut(id=row.id, time=row.time.strftime("%H:%M"))


@router.get("/notification-times", response_model=list[NotificationTimeOut])
async def list_notification_times(
    session: AsyncSession = Depends(get_session),
) -> list[NotificationTimeOut]:
    """Return the notification plan: all daily times, sorted ascending."""
    result = await session.execute(
        select(NotificationTime).order_by(NotificationTime.time)
    )
    return [_to_out(row) for row in result.scalars().all()]


@router.post(
    "/notification-times",
    response_model=NotificationTimeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification_time(
    body: NotificationTimeCreate,
    session: AsyncSession = Depends(get_session),
) -> NotificationTimeOut:
    """Add a daily notification time (HH:MM). 422 on invalid format, 409 on duplicate."""
    time_value = datetime.time.fromisoformat(body.time)

    result = await session.execute(
        select(NotificationTime).where(NotificationTime.time == time_value)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Notification time {body.time} already exists.",
        )

    row = NotificationTime(time=time_value)
    session.add(row)
    try:
        await session.commit()
    except IntegrityError:
        # Lost a race against a concurrent create — the DB unique constraint
        # on time is authoritative; report the same 409 as the pre-check.
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Notification time {body.time} already exists.",
        )
    await session.refresh(row)

    await notifications.reschedule_notification_times()
    return _to_out(row)


@router.delete("/notification-times/{time_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_time(
    time_id: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Remove a daily notification time. 404 if it does not exist."""
    row = await session.get(NotificationTime, time_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification time not found.",
        )

    await session.delete(row)
    await session.commit()

    await notifications.reschedule_notification_times()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notifications/connection-info", response_model=ConnectionInfoOut)
async def get_connection_info() -> ConnectionInfoOut:
    """Return the ntfy public URL and topic for the phone-app subscription hint."""
    ntfy = load_ntfy_settings()
    return ConnectionInfoOut(public_url=ntfy.ntfy_public_url, topic=ntfy.ntfy_topic)
