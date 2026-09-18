from __future__ import annotations

import pytest

from eloverblik_mcp.client import Aggregation, EloverblikClient, TimeSeriesRequest
from eloverblik_mcp.config import Settings


def make_client() -> EloverblikClient:
    settings = Settings(api_refresh_token="refresh", metering_point_id="1234567890123")
    return EloverblikClient(settings)


def test_get_time_series_adjusts_end_date_and_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client()

    captured: dict = {}

    def fake_request(method: str, path: str, **kwargs: dict) -> dict:
        captured["method"] = method
        captured["path"] = path
        captured["json"] = kwargs.get("json")
        return {"ok": True}

    monkeypatch.setattr(EloverblikClient, "access_token", "token")
    monkeypatch.setattr(client, "_request", fake_request)

    result = client.get_time_series(
        "9876543210000",
        TimeSeriesRequest(
            start_date="2024-01-01",
            end_date="2024-01-31",
            aggregation=Aggregation.DAY,
        ),
    )

    assert result == {"ok": True}
    assert captured["method"] == "POST"
    assert captured["path"] == "/meterdata/gettimeseries/2024-01-01/2024-02-01/Day"
    assert captured["json"] == {
        "meteringPoints": {"meteringPoint": ["9876543210000"]}
    }


def test_get_time_series_rejects_invalid_date_order(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client()
    monkeypatch.setattr(EloverblikClient, "access_token", "token")

    with pytest.raises(ValueError, match="end_date must be greater than or equal"):
        client.get_time_series(
            "9876543210000",
            TimeSeriesRequest(start_date="2024-01-02", end_date="2024-01-01"),
        )
