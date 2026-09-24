"""
Config loading for kwh-meter backend.

The path to the meter JSON config file is read from the KWH_METER_CONFIG
environment variable. The application refuses to start if the variable is
missing, the file does not exist, or the file contains invalid / incomplete
JSON. All five fields are required — no defaults are provided.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MeterConfig(BaseModel):
    """Domain model for the meter JSON config file."""

    zaehler_nr: str
    street: str
    house_number: str
    postal_code: str
    city: str

    @field_validator("zaehler_nr", "street", "house_number", "postal_code", "city")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("field must not be empty")
        return v


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kwh_meter_config: str  # path to the JSON config file


class NtfySettings(BaseSettings):
    """ntfy connection settings loaded from environment variables (with defaults)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Internal URL used by the backend to publish (compose network).
    ntfy_url: str = "http://ntfy:80"
    # Externally reachable URL of the ntfy server, shown in the web UI.
    ntfy_public_url: str = "http://localhost:8080"
    # Topic to publish to (and to subscribe to in the ntfy phone app).
    ntfy_topic: str = "kwh-meter-readings"


def load_ntfy_settings() -> NtfySettings:
    """Load the ntfy settings from the environment (falls back to defaults)."""
    return NtfySettings()


def load_meter_config() -> MeterConfig:
    """
    Load and validate the meter configuration from the JSON file whose path
    is specified by the KWH_METER_CONFIG environment variable.

    Raises RuntimeError on any configuration problem so the application
    refuses to start with a clear error message.
    """
    raw = os.environ.get("KWH_METER_CONFIG")
    if not raw:
        raise RuntimeError(
            "KWH_METER_CONFIG environment variable is not set. "
            "Provide the path to the meter JSON config file."
        )

    config_path = Path(raw)
    if not config_path.exists():
        raise RuntimeError(
            f"Meter config file not found: {config_path}. "
            "Check that KWH_METER_CONFIG points to an existing file."
        )

    try:
        with config_path.open() as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Meter config file is not valid JSON: {config_path}. "
            f"Parse error: {exc}"
        ) from exc

    try:
        return MeterConfig(**data)
    except Exception as exc:
        raise RuntimeError(
            f"Meter config file is missing required fields or has invalid values: {exc}"
        ) from exc
