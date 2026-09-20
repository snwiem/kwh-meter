"""Tests for GET /api/export/tsv and GET /api/export/json."""

from __future__ import annotations

import json

import pytest
from httpx import AsyncClient

READING_1 = {
    "timestamp": "2024-01-15T08:30:00+00:00",
    "value_kwh": 1000.5,
    "comment": None,
}
READING_2 = {
    "timestamp": "2024-06-01T14:00:00+00:00",
    "value_kwh": 1500.0,
    "comment": "Auto lädt",
}


@pytest.mark.asyncio
async def test_tsv_no_readings_returns_header_only(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/export/tsv")
    assert response.status_code == 200
    lines = response.text.splitlines()
    assert len(lines) == 1
    assert lines[0] == "zaehler_nr\ttimestamp\tvalue_kwh\tcomment"


@pytest.mark.asyncio
async def test_tsv_correct_columns_and_format(test_client: AsyncClient) -> None:
    await test_client.post("/api/readings", json=READING_1)
    await test_client.post("/api/readings", json=READING_2)

    response = await test_client.get("/api/export/tsv")
    assert response.status_code == 200
    lines = response.text.splitlines()
    # header + 2 data rows (sorted ascending by timestamp)
    assert len(lines) == 3
    cols = lines[1].split("\t")
    assert cols[0] == "DE00012345678901234567890"
    assert cols[2] == "1000.5"
    assert cols[3] == ""  # null comment → empty string


@pytest.mark.asyncio
async def test_tsv_timestamp_german_format(test_client: AsyncClient) -> None:
    await test_client.post("/api/readings", json=READING_1)

    response = await test_client.get("/api/export/tsv")
    lines = response.text.splitlines()
    ts_col = lines[1].split("\t")[1]
    assert ts_col == "15.01.2024 08:30"


@pytest.mark.asyncio
async def test_tsv_content_disposition(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/export/tsv")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "readings.tsv" in response.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_json_no_readings_returns_empty_array(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/export/json")
    assert response.status_code == 200
    data = json.loads(response.text)
    assert data == []


@pytest.mark.asyncio
async def test_json_correct_fields(test_client: AsyncClient) -> None:
    await test_client.post("/api/readings", json=READING_1)
    await test_client.post("/api/readings", json=READING_2)

    response = await test_client.get("/api/export/json")
    assert response.status_code == 200
    data = json.loads(response.text)
    assert len(data) == 2
    first = data[0]
    assert first["zaehler_nr"] == "DE00012345678901234567890"
    assert first["value_kwh"] == 1000.5
    assert first["comment"] is None
    # ISO 8601 format YYYY-MM-DDTHH:MM:SS
    assert first["timestamp"] == "2024-01-15T08:30:00"


@pytest.mark.asyncio
async def test_json_comment_present(test_client: AsyncClient) -> None:
    await test_client.post("/api/readings", json=READING_1)
    await test_client.post("/api/readings", json=READING_2)

    response = await test_client.get("/api/export/json")
    data = json.loads(response.text)
    second = data[1]
    assert second["comment"] == "Auto lädt"


@pytest.mark.asyncio
async def test_json_content_disposition(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/export/json")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "readings.json" in response.headers.get("content-disposition", "")
