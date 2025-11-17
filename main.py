"""Eloverblik API MCP Server

This MCP server provides tools to interact with the Danish Eloverblik API
for accessing electricity consumption data.
"""

import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache

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
API_REFRESH_TOKEN = os.getenv("API_REFRESH_TOKEN", "")
METERING_POINT_ID = os.getenv("METERING_POINT_ID", "")

# API endpoints
ELOVERBLIK_BASE_URL = "https://api.eloverblik.dk/customerapi/api"


@lru_cache(maxsize=1)
def fetch_access_token(api_refresh_token: str) -> str:
    """Fetch a new access token using the provided API refresh token.

    Args:
        api_refresh_token: The refresh token for the Eloverblik API

    Returns:
        The access token to use for API requests

    Raises:
        ValueError: If the token fetch fails or returns invalid data
        requests.HTTPError: If the API request fails
    """
    headers = {
        "Authorization": f"Bearer {api_refresh_token}",
        "api-version": "1.0",
        "accept": "application/json",
    }
    try:
        response = requests.get(
            f"{ELOVERBLIK_BASE_URL}/token", headers=headers, timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("result"):
            raise ValueError(
                "Failed to fetch access token. Check the refresh token or API response."
            )

        logger.info("Successfully fetched access token")
        return data["result"]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch access token: {e}")
        raise


@lru_cache(maxsize=1)
def get_api_credentials() -> tuple[str, str]:
    """Fetch and cache the API access token and metering point ID.

    Returns:
        Tuple of (access_token, metering_point_id)

    Raises:
        ValueError: If required environment variables are missing
    """
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
    """Check if the Eloverblik API is alive and accessible.

    Returns:
        API status information as a dictionary

    Raises:
        ValueError: If credentials are missing or invalid
        requests.HTTPError: If the API request fails
    """
    try:
        access_token, _ = get_api_credentials()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{ELOVERBLIK_BASE_URL}/isalive", headers=headers, timeout=30
        )
        response.raise_for_status()
        logger.info("API is alive")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to check API status: {e}")
        raise


@mcp.tool()
def eloverblik_metering_points(include_all: bool = False) -> dict:
    """Fetch a list of metering points associated with your account.

    Args:
        include_all: Include all metering points (past and present). Default is False.

    Returns:
        Dictionary containing list of metering points with their details

    Raises:
        ValueError: If credentials are missing or invalid
        requests.HTTPError: If the API request fails
    """
    try:
        access_token, _ = get_api_credentials()
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "api-version": "1.0",
        }
        params = {"includeAll": str(include_all).lower()}
        response = requests.get(
            f"{ELOVERBLIK_BASE_URL}/meteringpoints/meteringpoints",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        logger.info(f"Fetched metering points (include_all={include_all})")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch metering points: {e}")
        raise


class Aggregation(str, Enum):
    """Time aggregation levels for electricity consumption data."""

    ACTUAL = "Actual"
    QUARTER = "Quarter"
    HOUR = "Hour"
    DAY = "Day"
    MONTH = "Month"
    YEAR = "Year"


@mcp.tool()
def eloverblik_timeseries(
    start_date: str, end_date: str, aggregation: Aggregation = Aggregation.HOUR
) -> dict:
    """Fetch electricity consumption time series data for a date range.

    The end_date is automatically adjusted by +1 day to account for UTC time handling
    in the Eloverblik API, ensuring complete data for the requested period.

    Args:
        start_date: Start date in YYYY-MM-DD format (e.g., "2024-01-01")
        end_date: End date in YYYY-MM-DD format (e.g., "2024-01-31")
        aggregation: Time aggregation level (Actual, Quarter, Hour, Day, Month, Year).
                    Default is Hour.

    Returns:
        Dictionary containing time series consumption data

    Raises:
        ValueError: If credentials are missing, invalid, or date format is incorrect
        requests.HTTPError: If the API request fails

    Example:
        Get hourly consumption for January 2024:
        eloverblik_timeseries("2024-01-01", "2024-01-31", Aggregation.HOUR)
    """
    try:
        access_token, metering_point_id = get_api_credentials()
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "api-version": "1.0",
            "Content-Type": "application/json",
        }

        # Adjust end_date to account for UTC time handling
        adjusted_end_date = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        url = f"{ELOVERBLIK_BASE_URL}/meterdata/gettimeseries/{start_date}/{adjusted_end_date}/{aggregation.value}"
        payload = {"meteringPoints": {"meteringPoint": [metering_point_id]}}

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        logger.info(
            f"Fetched timeseries data from {start_date} to {end_date} "
            f"with {aggregation.value} aggregation"
        )
        return response.json()
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to fetch timeseries data: {e}")
        raise


if __name__ == "__main__":
    logging.info("Starting the Eloverblik MCP Server...")
    mcp.run()
