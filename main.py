import logging
import os
from enum import Enum

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the MCP server
mcp = FastMCP("Eloverblik Server")

load_dotenv(override=True)

TOKEN = os.getenv("TOKEN", "")
METERING_POINT_ID = os.getenv("METERING_POINT_ID", "")


@mcp.tool()
def eloverblik_isalive() -> dict:
    """Fetch data from the eloverblik.dk API."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(
        "https://api.eloverblik.dk/customerapi/api/isalive", headers=headers
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def eloverblik_metering_points(include_all: bool = False) -> dict:
    """Fetch a list of metering points from the eloverblik.dk API."""
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
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
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
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
