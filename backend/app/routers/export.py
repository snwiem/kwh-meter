"""Export router — GET /api/export/tsv and GET /api/export/json."""

from __future__ import annotations

import io
import json

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Reading

router = APIRouter(prefix="/api/export", tags=["export"])

_TSV_HEADER = "zaehler_nr\ttimestamp\tvalue_kwh\tcomment\n"


def _format_ts_german(ts: object) -> str:
    """Format a datetime as DD.MM.YYYY HH:MM."""
    from datetime import datetime as dt

    if isinstance(ts, dt):
        return ts.strftime("%d.%m.%Y %H:%M")
    return str(ts)


def _format_ts_iso(ts: object) -> str:
    """Format a datetime as YYYY-MM-DDTHH:MM:SS (no timezone, no microseconds)."""
    from datetime import datetime as dt

    if isinstance(ts, dt):
        return ts.strftime("%Y-%m-%dT%H:%M:%S")
    return str(ts)


async def _fetch_all_readings(
    session: AsyncSession, zaehler_nr: str
) -> list[Reading]:
    result = await session.execute(
        select(Reading)
        .where(Reading.zaehler_nr == zaehler_nr)
        .order_by(Reading.timestamp.asc())
    )
    return list(result.scalars().all())


@router.get("/tsv")
async def export_tsv(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """Download all readings for the active meter as a TSV file."""
    zaehler_nr: str = request.app.state.active_zaehler_nr
    readings = await _fetch_all_readings(session, zaehler_nr)

    def generate():
        yield _TSV_HEADER
        for r in readings:
            comment = r.comment if r.comment is not None else ""
            yield (
                f"{r.zaehler_nr}\t"
                f"{_format_ts_german(r.timestamp)}\t"
                f"{float(r.value_kwh):.1f}\t"
                f"{comment}\n"
            )

    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    filename = f"{zaehler_nr}-{now}.tsv"
    return StreamingResponse(
        generate(),
        media_type="text/tab-separated-values; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/json")
async def export_json(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Download all readings for the active meter as a JSON file."""
    zaehler_nr: str = request.app.state.active_zaehler_nr
    readings = await _fetch_all_readings(session, zaehler_nr)

    data = [
        {
            "zaehler_nr": r.zaehler_nr,
            "timestamp": _format_ts_iso(r.timestamp),
            "value_kwh": float(r.value_kwh),
            "comment": r.comment,
        }
        for r in readings
    ]

    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    filename = f"{zaehler_nr}-{now}.json"
    return Response(
        content=json.dumps(data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
