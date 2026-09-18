from __future__ import annotations

from dataclasses import dataclass

from eloverblik_mcp.client import Aggregation
from eloverblik_mcp.config import Settings
from eloverblik_mcp import server


@dataclass
class FakeClient:
    def is_alive(self) -> dict:
        return {"alive": True}

    def get_metering_points(self, include_all: bool = False) -> dict:
        return {"include_all": include_all}

    def get_time_series(self, metering_point_id: str, request) -> dict:
        return {
            "metering_point_id": metering_point_id,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "aggregation": request.aggregation.value,
        }


def test_new_and_legacy_tools_share_behavior(monkeypatch) -> None:
    fake_client = FakeClient()
    monkeypatch.setattr(server, "get_client", lambda: fake_client)
    monkeypatch.setattr(
        server,
        "get_settings",
        lambda: Settings(api_refresh_token="refresh", metering_point_id="1234"),
    )

    assert server.is_alive() == server.eloverblik_isalive() == {"alive": True}
    assert server.list_metering_points(True) == server.eloverblik_metering_points(True) == {
        "include_all": True
    }

    expected = {
        "metering_point_id": "1234",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "aggregation": Aggregation.HOUR.value,
    }
    assert server.get_time_series("2024-01-01", "2024-01-31") == expected
    assert (
        server.eloverblik_timeseries("2024-01-01", "2024-01-31", Aggregation.HOUR)
        == expected
    )
