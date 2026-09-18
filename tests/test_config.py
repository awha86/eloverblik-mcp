from __future__ import annotations

import pytest

from eloverblik_mcp.config import ConfigError, load_settings_from_mapping


def test_load_settings_from_mapping_requires_token_and_metering_point() -> None:
    with pytest.raises(ConfigError, match="API_REFRESH_TOKEN"):
        load_settings_from_mapping({"METERING_POINT_ID": "123"})


def test_load_settings_from_mapping_supports_optional_overrides() -> None:
    settings = load_settings_from_mapping(
        {
            "API_REFRESH_TOKEN": "refresh",
            "METERING_POINT_ID": "123",
            "ELOVERBLIK_BASE_URL": "https://example.test/api",
            "ELOVERBLIK_API_VERSION": "2.0",
            "ELOVERBLIK_TIMEOUT_SECONDS": "5",
        }
    )

    assert settings.base_url == "https://example.test/api"
    assert settings.api_version == "2.0"
    assert settings.timeout_seconds == 5
