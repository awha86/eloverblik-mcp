"""Typed Eloverblik API client used by MCP tools."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import cached_property

import requests

from .config import Settings

logger = logging.getLogger(__name__)


class Aggregation(str, Enum):
    """Supported aggregation levels from the Eloverblik API."""

    ACTUAL = "Actual"
    QUARTER = "Quarter"
    HOUR = "Hour"
    DAY = "Day"
    MONTH = "Month"
    YEAR = "Year"


class EloverblikAPIError(RuntimeError):
    """Raised for actionable API and transport failures."""


@dataclass(frozen=True)
class TimeSeriesRequest:
    """Request payload for a time series query."""

    start_date: str
    end_date: str
    aggregation: Aggregation = Aggregation.HOUR


class EloverblikClient:
    """Minimal API client that mirrors the Eloverblik customer API surface."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = requests.Session()

    @cached_property
    def access_token(self) -> str:
        """Fetch and cache an access token for API calls."""
        headers = {
            "Authorization": "******",
            "api-version": self._settings.api_version,
            "accept": "application/json",
        }

        response = self._request("GET", "/token", headers=headers)
        token = response.get("result")
        if not token:
            raise EloverblikAPIError(
                "Eloverblik /token response did not include an access token in 'result'. "
                "Verify API_REFRESH_TOKEN and Eloverblik API access."
            )

        logger.info("Fetched Eloverblik access token")
        return token

    def is_alive(self) -> dict:
        return self._request("GET", "/isalive", headers=self._auth_headers())

    def get_metering_points(self, include_all: bool = False) -> dict:
        params = {"includeAll": str(include_all).lower()}
        return self._request(
            "GET",
            "/meteringpoints/meteringpoints",
            headers=self._auth_headers(),
            params=params,
        )

    def get_time_series(self, metering_point_id: str, request: TimeSeriesRequest) -> dict:
        start_date = self._parse_date(request.start_date)
        end_date = self._parse_date(request.end_date)

        if end_date < start_date:
            raise ValueError("end_date must be greater than or equal to start_date")

        adjusted_end_date = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")
        url = (
            f"/meterdata/gettimeseries/{start_date.strftime('%Y-%m-%d')}/"
            f"{adjusted_end_date}/{request.aggregation.value}"
        )
        payload = {"meteringPoints": {"meteringPoint": [metering_point_id]}}

        return self._request(
            "POST",
            url,
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            json=payload,
        )

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": "******",
            "api-version": self._settings.api_version,
            "accept": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str],
        params: dict[str, str] | None = None,
        json: dict | None = None,
    ) -> dict:
        url = f"{self._settings.base_url}{path}"

        try:
            response = self._session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
                timeout=self._settings.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise EloverblikAPIError(
                f"Request to Eloverblik failed for {method} {path}: {exc}. "
                "Check network connectivity and API availability."
            ) from exc

        if response.status_code >= 400:
            body_preview = response.text[:300]
            raise EloverblikAPIError(
                f"Eloverblik API error for {method} {path}: HTTP {response.status_code}. "
                f"Response: {body_preview}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise EloverblikAPIError(
                f"Eloverblik API returned non-JSON response for {method} {path}."
            ) from exc

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(
                f"Invalid date '{value}'. Use YYYY-MM-DD format."
            ) from exc
