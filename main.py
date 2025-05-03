import logging
import os
from enum import Enum
from functools import lru_cache

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the MCP server
mcp = FastMCP("Eloverblik Server")

load_dotenv(override=True)

API_REFRESH_TOKEN = os.getenv("API_REFRESH_TOKEN", "")
METERING_POINT_ID = os.getenv("METERING_POINT_ID", "")


@lru_cache(maxsize=1)
def fetch_access_token(api_refresh_token: str) -> str:
    """Fetch a new access token using the provided API refresh token."""
    headers = {
        "Authorization": f"Bearer {api_refresh_token}",
        "api-version": "1.0",
        "accept": "application/json",
    }
    response = requests.get(
        "https://api.eloverblik.dk/customerapi/api/token", headers=headers
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("result"):
        raise ValueError(
            "Failed to fetch access token. Check the refresh token or API response."
        )

    return data["result"]


@lru_cache(maxsize=1)
def get_api_credentials():
    """Fetch and cache the API access token and metering point ID."""
    api_refresh_token = os.getenv("API_REFRESH_TOKEN", "")
    metering_point_id = os.getenv("METERING_POINT_ID", "")

    if not api_refresh_token or not metering_point_id:
        raise ValueError(
            "Missing API_REFRESH_TOKEN or METERING_POINT_ID in environment variables."
        )

    access_token = fetch_access_token(api_refresh_token)
    return access_token, metering_point_id


@mcp.tool()
def eloverblik_isalive() -> dict:
    """Fetch data from the eloverblik.dk API."""
    access_token, _ = get_api_credentials()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://api.eloverblik.dk/customerapi/api/isalive", headers=headers
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def eloverblik_metering_points(include_all: bool = False) -> dict:
    """Fetch a list of metering points from the eloverblik.dk API."""
    access_token, _ = get_api_credentials()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "api-version": "1.0",
    }
    params = {"includeAll": str(include_all).lower()}
    response = requests.get(
        "https://api.eloverblik.dk/customerapi/api/meteringpoints/meteringpoints",
        headers=headers,
        params=params,
    )
    response.raise_for_status()
    return response.json()


class Aggregation(str, Enum):
    ACTUAL = "Actual"
    QUARTER = "Quarter"
    HOUR = "Hour"
    DAY = "Day"
    MONTH = "Month"
    YEAR = "Year"


@mcp.tool()
def eloverblik_timeseries(
    start_date: str, end_date: str, metering_point_ids: list, aggregation: Aggregation
) -> dict:
    """Fetch time series data from the eloverblik.dk API."""
    access_token, _ = get_api_credentials()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "api-version": "1.0",
        "Content-Type": "application/json",
    }
    url = f"https://api.eloverblik.dk/customerapi/api/meterdata/gettimeseries/{start_date}/{end_date}/{aggregation.value}"
    payload = {"meteringPoints": {"meteringPoint": metering_point_ids}}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    logging.info("Starting the Eloverblik MCP Server...")
    mcp.run()
