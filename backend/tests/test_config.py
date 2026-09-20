"""
Tests for meter config loading (app/config.py).

These tests exercise the startup validation logic directly, without
starting the full FastAPI app.
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from app.config import load_meter_config, MeterConfig


class TestLoadMeterConfigEnvVar:
    def test_raises_if_env_var_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """App must refuse to start when KWH_METER_CONFIG is not set."""
        monkeypatch.delenv("KWH_METER_CONFIG", raising=False)
        with pytest.raises(RuntimeError, match="KWH_METER_CONFIG"):
            load_meter_config()

    def test_raises_if_env_var_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An empty string is treated the same as unset."""
        monkeypatch.setenv("KWH_METER_CONFIG", "")
        with pytest.raises(RuntimeError, match="KWH_METER_CONFIG"):
            load_meter_config()


class TestLoadMeterConfigFile:
    def test_raises_if_file_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """App must refuse to start when the config file does not exist."""
        monkeypatch.setenv("KWH_METER_CONFIG", "/nonexistent/path/meter.json")
        with pytest.raises(RuntimeError, match="not found"):
            load_meter_config()

    def test_raises_if_file_malformed_json(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        """App must refuse to start when the config file is not valid JSON."""
        bad_file = tmp_path / "meter.json"
        bad_file.write_text("{ this is not json }")
        monkeypatch.setenv("KWH_METER_CONFIG", str(bad_file))
        with pytest.raises(RuntimeError, match="not valid JSON"):
            load_meter_config()

    def test_raises_if_required_field_missing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        """App must refuse to start when a required field is absent."""
        incomplete = {
            "zaehler_nr": "DE00012345678901234567890",
            "street": "Musterstraße",
            # house_number, postal_code, city are missing
        }
        bad_file = tmp_path / "meter.json"
        bad_file.write_text(json.dumps(incomplete))
        monkeypatch.setenv("KWH_METER_CONFIG", str(bad_file))
        with pytest.raises(RuntimeError, match="missing required fields"):
            load_meter_config()

    def test_raises_if_field_is_empty_string(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        """Empty string values must be rejected as invalid."""
        data = {
            "zaehler_nr": "",
            "street": "Musterstraße",
            "house_number": "1",
            "postal_code": "12345",
            "city": "Musterstadt",
        }
        bad_file = tmp_path / "meter.json"
        bad_file.write_text(json.dumps(data))
        monkeypatch.setenv("KWH_METER_CONFIG", str(bad_file))
        with pytest.raises(RuntimeError):
            load_meter_config()

    def test_valid_config_returns_meter_config(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        """A fully valid config file should load without error."""
        data = {
            "zaehler_nr": "DE00012345678901234567890",
            "street": "Musterstraße",
            "house_number": "42",
            "postal_code": "12345",
            "city": "Musterstadt",
        }
        config_file = tmp_path / "meter.json"
        config_file.write_text(json.dumps(data))
        monkeypatch.setenv("KWH_METER_CONFIG", str(config_file))

        result = load_meter_config()

        assert isinstance(result, MeterConfig)
        assert result.zaehler_nr == data["zaehler_nr"]
        assert result.street == data["street"]
        assert result.house_number == data["house_number"]
        assert result.postal_code == data["postal_code"]
        assert result.city == data["city"]


# Allow Any type hint in test params without import
from typing import Any  # noqa: E402
