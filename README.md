# eloverblik-mcp

A production-focused [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for the Danish [Eloverblik Customer API](https://api.eloverblik.dk/customerapi/index.html), implemented with [GoFastMCP / FastMCP](https://gofastmcp.com).

> Repository note: this repository is currently hosted as `awha86/eloverblik_api_mcp`. The project branding and package naming have been updated to `eloverblik-mcp` / `eloverblik_mcp`.

## What this server provides

This server mirrors a practical subset of the Eloverblik customer API as MCP tools:

| MCP tool | Eloverblik API surface | Purpose |
|---|---|---|
| `is_alive` | `GET /isalive` | Check API health/reachability |
| `list_metering_points` | `GET /meteringpoints/meteringpoints` | List account metering points |
| `get_time_series` | `POST /meterdata/gettimeseries/{from}/{to}/{aggregation}` | Fetch consumption time series |

Backward-compatible aliases are also available:
- `eloverblik_isalive`
- `eloverblik_metering_points`
- `eloverblik_timeseries`

## Status and scope

- Uses a dedicated API client layer (`eloverblik_mcp.client`) and a separate MCP tool layer (`eloverblik_mcp.server`).
- Uses typed request handling for time series queries (`Aggregation`, `TimeSeriesRequest`).
- Adds actionable config/API errors for easier troubleshooting.
- Endpoint coverage is intentionally scoped to the current implemented subset; additional Swagger endpoints can be added incrementally in the same pattern.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Eloverblik API refresh token
- A metering point ID connected to your account

## Installation

```bash
git clone https://github.com/awha86/eloverblik_api_mcp.git
cd eloverblik_api_mcp
uv sync
```

## Configuration

Copy the example env file and populate it with your credentials:

```bash
cp .env.example .env
```

Required variables:

```env
API_REFRESH_TOKEN=your_refresh_token
METERING_POINT_ID=your_metering_point_id
```

Optional variables:

```env
ELOVERBLIK_BASE_URL=https://api.eloverblik.dk/customerapi/api
ELOVERBLIK_API_VERSION=1.0
ELOVERBLIK_TIMEOUT_SECONDS=30
```

## Run

```bash
uv run eloverblik-mcp
```

Backward-compatible entry point:

```bash
uv run main.py
```

## MCP client setup example (Claude Desktop)

```json
{
  "mcpServers": {
    "eloverblik": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/eloverblik_api_mcp",
        "run",
        "eloverblik-mcp"
      ]
    }
  }
}
```

## Developer workflow

Lint:

```bash
uv run ruff check .
```

Tests:

```bash
uv run pytest
```

## Error handling behavior

- Missing `API_REFRESH_TOKEN` / `METERING_POINT_ID` raises clear configuration errors with setup guidance.
- Transport/API failures include HTTP method/path and response preview to speed up diagnosis.
- Invalid dates return explicit `YYYY-MM-DD` guidance.

## Limitations

- Current endpoint coverage is a scoped subset of the full Customer API Swagger surface.
- Tool outputs are currently close to raw API payloads (intentional for traceability).
- Token refresh is process-cached; restart the process if long-running sessions require fresh state.

## Related links

- Eloverblik docs: https://api.eloverblik.dk/customerapi/index.html
- Swagger JSON: https://api.eloverblik.dk/customerapi/swagger/customerapi-v1.0/swagger.json
- GoFastMCP docs: https://gofastmcp.com/getting-started/welcome
