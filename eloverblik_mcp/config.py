"""Configuration helpers for the Eloverblik MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Mapping

from dotenv import load_dotenv


class ConfigError(ValueError):
    """Raised when required environment configuration is missing."""


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    api_refresh_token: str
    metering_point_id: str
    base_url: str = "https://api.eloverblik.dk/customerapi/api"
    api_version: str = "1.0"
    timeout_seconds: int = 30


def _clean(value: str | None) -> str:
    return (value or "").strip()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and validate settings from the process environment."""
    load_dotenv(override=True)

    api_refresh_token = _clean(os.getenv("API_REFRESH_TOKEN"))
    metering_point_id = _clean(os.getenv("METERING_POINT_ID"))

    missing: list[str] = []
    if not api_refresh_token:
        missing.append("API_REFRESH_TOKEN")
    if not metering_point_id:
        missing.append("METERING_POINT_ID")

    if missing:
        missing_fields = ", ".join(missing)
        raise ConfigError(
            f"Missing required environment variable(s): {missing_fields}. "
            "Create a .env file from .env.example and set these values from your "
            "Eloverblik account."
        )

    return Settings(
        api_refresh_token=api_refresh_token,
        metering_point_id=metering_point_id,
    )


def load_settings_from_mapping(env: Mapping[str, str | None]) -> Settings:
    """Load settings from a mapping, primarily for tests."""
    api_refresh_token = _clean(env.get("API_REFRESH_TOKEN"))
    metering_point_id = _clean(env.get("METERING_POINT_ID"))

    missing: list[str] = []
    if not api_refresh_token:
        missing.append("API_REFRESH_TOKEN")
    if not metering_point_id:
        missing.append("METERING_POINT_ID")

    if missing:
        missing_fields = ", ".join(missing)
        raise ConfigError(f"Missing required environment variable(s): {missing_fields}")

    return Settings(
        api_refresh_token=api_refresh_token,
        metering_point_id=metering_point_id,
        base_url=_clean(env.get("ELOVERBLIK_BASE_URL"))
        or "https://api.eloverblik.dk/customerapi/api",
        api_version=_clean(env.get("ELOVERBLIK_API_VERSION")) or "1.0",
        timeout_seconds=int(_clean(env.get("ELOVERBLIK_TIMEOUT_SECONDS")) or "30"),
    )
