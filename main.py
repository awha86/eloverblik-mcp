"""Eloverblik API MCP Server.

This MCP server provides tools that mirror the Eloverblik Customer API
surface described by its Swagger/OpenAPI specification.
"""

import logging
import os
import re
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

# Initialize the MCP server
mcp = FastMCP("Eloverblik API Server")

# API configuration from environment
ELOVERBLIK_BASE_URL = "https://api.eloverblik.dk/customerapi/api"
API_VERSION = "1.0"


class Aggregation(str, Enum):
    """Time aggregation levels for electricity consumption data."""

    ACTUAL = "Actual"
    QUARTER = "Quarter"
    HOUR = "Hour"
    DAY = "Day"
    MONTH = "Month"
    YEAR = "Year"


@lru_cache(maxsize=1)
def fetch_access_token(api_refresh_token: str) -> str:
    """Fetch a new access token using the provided API refresh token."""
    headers = {
        "Authorization": f"Bearer {api_refresh_token}",
        "api-version": API_VERSION,
        "accept": "application/json",
    }

    response = requests.get(f"{ELOVERBLIK_BASE_URL}/token", headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data.get("result"):
        raise ValueError(
            "Failed to fetch access token. Check the refresh token or API response."
        )

    logger.info("Successfully fetched access token")
    return data["result"]


@lru_cache(maxsize=1)
def get_access_token() -> str:
    """Return a cached access token derived from API_REFRESH_TOKEN."""
    api_refresh_token = os.getenv("API_REFRESH_TOKEN", "")
    if not api_refresh_token:
        raise ValueError("Missing API_REFRESH_TOKEN in environment variables.")
    return fetch_access_token(api_refresh_token)


def _build_headers(include_content_type: bool = False) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "accept": "application/json",
        "api-version": API_VERSION,
    }
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers


def _resolve_metering_point_ids(metering_point_ids: list[str] | None) -> list[str]:
    if metering_point_ids:
        cleaned_ids = [
            metering_point_id.strip() for metering_point_id in metering_point_ids
        ]
        cleaned_ids = [
            metering_point_id for metering_point_id in cleaned_ids if metering_point_id
        ]
        if cleaned_ids:
            return cleaned_ids

    default_metering_point_id = os.getenv("METERING_POINT_ID", "").strip()
    if not default_metering_point_id:
        raise ValueError(
            "Provide metering_point_ids or set METERING_POINT_ID in environment variables."
        )

    return [default_metering_point_id]


def _metering_points_payload(metering_point_ids: list[str] | None = None) -> dict:
    return {
        "meteringPoints": {
            "meteringPoint": _resolve_metering_point_ids(metering_point_ids)
        }
    }


def _request_json(
    method: str,
    endpoint: str,
    *,
    params: dict | None = None,
    json_body: dict | None = None,
) -> dict:
    response = requests.request(
        method=method,
        url=f"{ELOVERBLIK_BASE_URL}{endpoint}",
        headers=_build_headers(include_content_type=json_body is not None),
        params=params,
        json=json_body,
        timeout=30,
    )
    response.raise_for_status()

    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()

    try:
        return response.json()
    except ValueError:
        return {"result": response.text}


def _request_export(endpoint: str, payload: dict) -> dict:
    response = requests.request(
        method="POST",
        url=f"{ELOVERBLIK_BASE_URL}{endpoint}",
        headers=_build_headers(include_content_type=True),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()

    content_disposition = response.headers.get("content-disposition", "")
    filename_match = re.search(r'filename="?([^";]+)"?', content_disposition)

    return {
        "content_type": response.headers.get("content-type", "text/csv"),
        "filename": filename_match.group(1) if filename_match else None,
        "content": response.text,
    }


@mcp.tool()
def eloverblik_token(force_refresh: bool = False) -> dict:
    """Get a data access token from your configured API refresh token."""
    if force_refresh:
        fetch_access_token.cache_clear()
        get_access_token.cache_clear()

    return {"result": get_access_token()}


@mcp.tool()
def eloverblik_isalive() -> dict:
    """Check if the Eloverblik API is alive and accessible."""
    response = requests.request(
        method="GET",
        url=f"{ELOVERBLIK_BASE_URL}/isalive",
        headers={"accept": "application/json", "api-version": API_VERSION},
        timeout=30,
    )
    response.raise_for_status()

    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()

    return {"result": response.text.strip().lower() == "true"}


@mcp.tool()
def eloverblik_metering_points(include_all: bool = False) -> dict:
    """Fetch a list of metering points associated with your account."""
    params = {"includeAll": str(include_all).lower()}
    return _request_json("GET", "/meteringpoints/meteringpoints", params=params)


@mcp.tool()
def eloverblik_metering_point_relation_add(
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Add relation(s) to metering point(s) based on CPR/CVR ownership."""
    return _request_json(
        "POST",
        "/meteringpoints/meteringpoint/relation/add",
        json_body=_metering_points_payload(metering_point_ids),
    )


@mcp.tool()
def eloverblik_metering_point_relation_add_with_web_access_code(
    metering_point_id: str,
    web_access_code: str,
) -> dict:
    """Add relation to one metering point using metering point ID and web access code."""
    endpoint = (
        "/meteringpoints/meteringpoint/relation/add/"
        f"{quote(metering_point_id, safe='')}/{quote(web_access_code, safe='')}"
    )
    return _request_json("PUT", endpoint)


@mcp.tool()
def eloverblik_metering_point_relation_delete(metering_point_id: str) -> dict:
    """Delete relation to a metering point."""
    endpoint = (
        f"/meteringpoints/meteringpoint/relation/{quote(metering_point_id, safe='')}"
    )
    return _request_json("DELETE", endpoint)


@mcp.tool()
def eloverblik_metering_point_details(
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Get detailed information for one or more metering points."""
    return _request_json(
        "POST",
        "/meteringpoints/meteringpoint/getdetails",
        json_body=_metering_points_payload(metering_point_ids),
    )


@mcp.tool()
def eloverblik_metering_point_charges(
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Get current charges for one or more metering points."""
    return _request_json(
        "POST",
        "/meteringpoints/meteringpoint/getcharges",
        json_body=_metering_points_payload(metering_point_ids),
    )


@mcp.tool()
def eloverblik_masterdata_export(
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Export metering point master data as CSV content."""
    return _request_export(
        "/meteringpoints/masterdata/export",
        _metering_points_payload(metering_point_ids),
    )


@mcp.tool()
def eloverblik_charges_export(
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Export metering point charges as CSV content."""
    return _request_export(
        "/meteringpoints/charges/export",
        _metering_points_payload(metering_point_ids),
    )


@mcp.tool()
def eloverblik_timeseries(
    start_date: str,
    end_date: str,
    aggregation: Aggregation = Aggregation.HOUR,
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Fetch electricity consumption time series data for a date range."""
    adjusted_end_date = (
        datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    ).strftime("%Y-%m-%d")
    endpoint = (
        "/meterdata/gettimeseries/"
        f"{quote(start_date, safe='')}/{quote(adjusted_end_date, safe='')}/{quote(aggregation.value, safe='')}"
    )

    return _request_json(
        "POST",
        endpoint,
        json_body=_metering_points_payload(metering_point_ids),
    )


@mcp.tool()
def eloverblik_meter_readings(
    start_date: str,
    end_date: str,
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Fetch meter readings for one or more metering points and a date range."""
    endpoint = (
        "/meterdata/getmeterreadings/"
        f"{quote(start_date, safe='')}/{quote(end_date, safe='')}"
    )

    return _request_json(
        "POST",
        endpoint,
        json_body=_metering_points_payload(metering_point_ids),
    )


@mcp.tool()
def eloverblik_timeseries_export(
    start_date: str,
    end_date: str,
    aggregation: Aggregation = Aggregation.HOUR,
    metering_point_ids: list[str] | None = None,
) -> dict:
    """Export timeseries data as CSV content for one or more metering points."""
    endpoint = (
        "/meterdata/timeseries/export/"
        f"{quote(start_date, safe='')}/{quote(end_date, safe='')}/{quote(aggregation.value, safe='')}"
    )

    return _request_export(endpoint, _metering_points_payload(metering_point_ids))


if __name__ == "__main__":
    logger.info("Starting the Eloverblik MCP Server...")
    mcp.run()
