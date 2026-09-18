# Eloverblik API MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for interacting with the Danish [Eloverblik API](https://api.eloverblik.dk/), built with [FastMCP](https://github.com/jlowin/fastmcp).

## Overview

This MCP server provides tools to access electricity consumption data from the Danish national energy grid through the Eloverblik API. It enables AI assistants to fetch and analyze your energy usage patterns.

## Features

- 🔌 **API Health + Auth** - Check API status and fetch access tokens
- 📊 **Metering Point Operations** - List points, add/delete relations, fetch details and charges
- 📈 **Meter Data Operations** - Retrieve time series, meter readings, and CSV exports
- 📁 **CSV Export Operations** - Export timeseries, master data, and charges
- 🔐 **Automatic Authentication** - Uses your refresh token for authenticated endpoints
- 📝 **Comprehensive Logging** - Detailed logging for debugging and monitoring

## Requirements

- Python 3.13+ (recommended) or Python 3.10+
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- An active Eloverblik API refresh token (see [Configuration](#configuration))

## Installation

### 1. Install uv

First, install [uv](https://docs.astral.sh/uv/) if you haven't already:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Using pip (alternative)
pip install uv
```

### 2. Clone the Repository

```bash
git clone https://github.com/awha86/eloverblik-mcp.git
cd eloverblik-mcp
```

### 3. Install Dependencies

```bash
# Create virtual environment and install dependencies
uv sync
```

This will:
- Create a virtual environment in `.venv/`
- Install all project dependencies from `pyproject.toml`
- Lock dependencies in `uv.lock` for reproducible builds

## Configuration

### Getting Your Eloverblik Credentials

1. **Get API Refresh Token**: Visit [Eloverblik](https://eloverblik.dk/) and log in to generate your API refresh token
2. **Find Metering Point ID**: Your metering point ID can be found on your electricity bill or through the Eloverblik website

### Environment Setup

Create a `.env` file in the project root based on `.env_example`:

```bash
cp .env_example .env
```

Edit the `.env` file and add your credentials:

```env
API_REFRESH_TOKEN=your_actual_refresh_token_here
METERING_POINT_ID=your_metering_point_id_here
```

⚠️ **Security Note**: Never commit your `.env` file to version control. It's already listed in `.gitignore`.

## MCP Client Configuration

### Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "eloverblik": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/eloverblik-mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

### Visual Studio Code

This repository includes a workspace-scoped configuration at
`.vscode/mcp.json`. Open the repository folder in VS Code, then run
**Developer: Reload Window** from the Command Palette to load it.

VS Code's current MCP configuration format uses `mcp.json`, rather than the
general `settings.json` entry used by older releases. The included
configuration runs the server from the opened workspace:

```json
{
  "servers": {
    "eloverblik": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "${workspaceFolder}",
        "run",
        "main.py"
      ]
    }
  }
}
```

To make the server available from every VS Code workspace, run **MCP: Open
User Configuration** from the Command Palette and copy the same `servers`
object into the user-level `mcp.json` file. Change `${workspaceFolder}` to an
absolute path in that case.


## Usage

Once configured, the MCP server provides the following tools to your AI assistant:

### Swagger Coverage

The server mirrors all endpoints listed in the Eloverblik customer API swagger
(`customerapi-v1.0`): `13/13` endpoint paths are represented as MCP tools.

### Available Tools

1. **eloverblik_token** - Get/refresh data access token
2. **eloverblik_isalive** - Check API connectivity
3. **eloverblik_metering_points** - List metering points
4. **eloverblik_metering_point_relation_add** - Add relation(s) by ownership
5. **eloverblik_metering_point_relation_add_with_web_access_code** - Add relation with web access code
6. **eloverblik_metering_point_relation_delete** - Delete a relation
7. **eloverblik_metering_point_details** - Fetch metering point details
8. **eloverblik_metering_point_charges** - Fetch metering point charges
9. **eloverblik_masterdata_export** - Export master data CSV
10. **eloverblik_charges_export** - Export charges CSV
11. **eloverblik_timeseries** - Fetch timeseries data
12. **eloverblik_meter_readings** - Fetch meter readings data
13. **eloverblik_timeseries_export** - Export timeseries CSV

### Example Prompts

Ask your AI assistant in natural language. It selects the appropriate MCP
tool and supplies its arguments. The following prompts cover every available
tool.

For tools that accept metering-point IDs, you can omit the ID to use the
`METERING_POINT_ID` configured in your `.env` file. Replace the example ID
`YOUR_METERING_POINT_ID` with your own when requesting another metering point.

#### Authentication and connectivity

- **eloverblik_token**
  - "Get my Eloverblik access token."
  - "Force-refresh my Eloverblik access token."
- **eloverblik_isalive**
  - "Check whether the Eloverblik API is online."
  - "Test my Eloverblik API connection."

#### Metering points and relations

- **eloverblik_metering_points**
  - "List my electricity metering points."
  - "Show all metering points, including moved-out points."
- **eloverblik_metering_point_relation_add**
  - "Add my metering-point relations."
  - "Add the relation for metering point YOUR_METERING_POINT_ID."
  - "Add relations for metering points YOUR_METERING_POINT_ID and ANOTHER_METERING_POINT_ID."
- **eloverblik_metering_point_relation_add_with_web_access_code**
  - "Add metering point YOUR_METERING_POINT_ID using web access code YOUR_WEB_ACCESS_CODE."
  - "Connect metering point YOUR_METERING_POINT_ID with web access code YOUR_WEB_ACCESS_CODE."
- **eloverblik_metering_point_relation_delete**
  - "Remove my relation to metering point YOUR_METERING_POINT_ID."
  - "Delete the Eloverblik relation for metering point YOUR_METERING_POINT_ID."

#### Metering-point details and charges

- **eloverblik_metering_point_details**
  - "Show details for all my configured metering points."
  - "What is the meter number, address, supplier, and reading interval for YOUR_METERING_POINT_ID?"
- **eloverblik_metering_point_charges**
  - "Show the current charges for my electricity meter."
  - "What taxes, tariffs, and fees apply to metering point YOUR_METERING_POINT_ID?"
- **eloverblik_masterdata_export**
  - "Export my metering-point master data as CSV."
  - "Download CSV details for all my metering points."
- **eloverblik_charges_export**
  - "Export my electricity charges as CSV."
  - "Create a CSV containing all tariffs, taxes, and fees for my meters."

#### Consumption and meter readings

Dates must use the `YYYY-MM-DD` format. Time-series requests support
`Actual`, `Quarter`, `Hour`, `Day`, `Month`, and `Year` aggregations.

- **eloverblik_timeseries**
  - "What was my electricity consumption in April 2026?"
  - "Show my daily consumption from 2026-04-01 to 2026-04-30."
  - "Show hourly consumption for metering point YOUR_METERING_POINT_ID from 2026-04-01 to 2026-04-07."
  - "Show monthly consumption for all of 2025."
  - "Show actual meter-data intervals for 2026-04-01 to 2026-04-02."
- **eloverblik_meter_readings**
  - "Show my meter readings from 2026-04-01 to 2026-04-30."
  - "Get meter readings for YOUR_METERING_POINT_ID between 2026-01-01 and 2026-03-31."
  - "What were the start and end meter readings for April 2026?"
- **eloverblik_timeseries_export**
  - "Export my hourly electricity consumption from 2026-04-01 to 2026-04-30 as CSV."
  - "Export daily consumption for 2026-04-01 to 2026-04-30."
  - "Export monthly consumption for 2025 for metering point YOUR_METERING_POINT_ID."
  - "Download a CSV of my electricity time series using yearly aggregation."

## Development

### Running the Server Locally

Test the MCP server locally using the FastMCP development tools:

```bash
# Run the server in development mode
uv run main.py
```

Or use the FastMCP CLI:

```bash
# Install the server and run interactively
uv run fastmcp run main.py
```

### Project Structure

```
eloverblik-mcp/
├── main.py              # Main MCP server implementation
├── tests/
│   └── test_main.py     # Focused unit tests for MCP endpoint wrappers
├── pyproject.toml       # Project dependencies and metadata
├── uv.lock             # Locked dependency versions
├── .env_example        # Example environment variables
├── .env                # Your credentials (not in git)
└── README.md           # This file
```

### Adding Dependencies

To add new Python packages:

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Code Quality

The project uses Ruff for linting. Configuration is in `pyproject.toml`:

```bash
# Run linting (if ruff is installed)
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .
```

Run focused tests:

```bash
uv run python -m unittest tests/test_main.py
```

## Troubleshooting

### Common Issues

**Authentication Errors**
- Verify your `API_REFRESH_TOKEN` is valid and not expired
- Check that `METERING_POINT_ID` matches your account

**Connection Issues**
- Ensure you have internet connectivity
- Check if the Eloverblik API is operational: https://api.eloverblik.dk/

**MCP Client Not Finding Server**
- Verify the path in your MCP configuration is absolute
- Ensure `uv` is in your system PATH
- Check that `.env` file exists and contains valid credentials

### Debug Logging

The server logs detailed information to help troubleshoot issues. Check the console output when running the server for diagnostic information.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source. See the repository for license details.

## Related Links

- [Eloverblik API Documentation](https://api.eloverblik.dk/)
- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [uv Documentation](https://docs.astral.sh/uv/)