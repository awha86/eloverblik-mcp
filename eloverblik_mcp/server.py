"""GoFastMCP server and tool layer for Eloverblik."""

from __future__ import annotations

import logging
from functools import lru_cache

from fastmcp import FastMCP

from .client import Aggregation, EloverblikClient, TimeSeriesRequest
from .config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP("eloverblik-mcp")


@lru_cache(maxsize=1)
def get_client() -> EloverblikClient:
    return EloverblikClient(get_settings())


@mcp.tool()
def is_alive() -> dict:
    """Check if the Eloverblik API is reachable and healthy."""
    return get_client().is_alive()


@mcp.tool()
def list_metering_points(include_all: bool = False) -> dict:
    """List metering points available for the authenticated Eloverblik account."""
    return get_client().get_metering_points(include_all=include_all)


@mcp.tool()
def get_time_series(
    start_date: str,
    end_date: str,
    aggregation: Aggregation = Aggregation.HOUR,
) -> dict:
    """Get consumption time series for configured metering point and date range."""
    settings = get_settings()
    request = TimeSeriesRequest(
        start_date=start_date,
        end_date=end_date,
        aggregation=aggregation,
    )
    return get_client().get_time_series(settings.metering_point_id, request)


@mcp.tool()
def eloverblik_isalive() -> dict:
    """Compatibility alias for is_alive."""
    return is_alive()


@mcp.tool()
def eloverblik_metering_points(include_all: bool = False) -> dict:
    """Compatibility alias for list_metering_points."""
    return list_metering_points(include_all=include_all)


@mcp.tool()
def eloverblik_timeseries(
    start_date: str,
    end_date: str,
    aggregation: Aggregation = Aggregation.HOUR,
) -> dict:
    """Compatibility alias for get_time_series."""
    return get_time_series(start_date=start_date, end_date=end_date, aggregation=aggregation)


def main() -> None:
    logger.info("Starting eloverblik-mcp server")
    mcp.run()


if __name__ == "__main__":
    main()
