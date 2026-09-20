"""
FastAPI application entrypoint for kwh-meter.

Startup sequence:
  1. Load and validate the meter config from the JSON file pointed to by
     KWH_METER_CONFIG. Raises RuntimeError (→ process exits) if missing or
     invalid.
  2. Create all DB tables (idempotent; safe to run on every start).
  3. Upsert the configured meter into the DB so readings can be associated
     with it.
  4. Store the active zaehler_nr in app.state for use by request handlers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .config import load_meter_config
from . import database as db_module
from .database import Base
from .models import Meter, Reading  # noqa: F401 — Reading must be imported so Base.metadata includes the readings table
from .routers import export as export_router
from .routers import meter as meter_router
from .routers import readings as readings_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup tasks before yield, shutdown after."""
    # --- Startup ---
    # 1. Load config (raises RuntimeError → crashes process on bad config)
    meter_cfg = load_meter_config()

    # 2. Create tables (always read from db_module so tests can patch the engine)
    async with db_module.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 3. Upsert meter row
    async with db_module.AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Meter).where(Meter.zaehler_nr == meter_cfg.zaehler_nr)
            )
            existing = result.scalar_one_or_none()
            if existing is None:
                session.add(
                    Meter(
                        zaehler_nr=meter_cfg.zaehler_nr,
                        street=meter_cfg.street,
                        house_number=meter_cfg.house_number,
                        postal_code=meter_cfg.postal_code,
                        city=meter_cfg.city,
                    )
                )
            else:
                # Update address fields in case they changed (zaehler_nr is stable)
                existing.street = meter_cfg.street
                existing.house_number = meter_cfg.house_number
                existing.postal_code = meter_cfg.postal_code
                existing.city = meter_cfg.city

    # 4. Store active meter identity for request handlers
    application.state.active_zaehler_nr = meter_cfg.zaehler_nr

    yield
    # --- Shutdown (nothing to clean up for now) ---


app = FastAPI(title="kWh Meter API", version="0.1.0", lifespan=lifespan)

app.include_router(meter_router.router)
app.include_router(readings_router.router)
app.include_router(export_router.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
