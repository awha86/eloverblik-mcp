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
git clone https://github.com/awha86/eloverblik_api_mcp.git
cd eloverblik_api_mcp
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
        "/absolute/path/to/eloverblik_api_mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

### Visual Studio Code

1. Open VS Code settings by pressing `Ctrl/Cmd + Shift + P` and typing `Preferences: Open User Settings (JSON)`

2. Add the MCP server configuration:

**Windows**:
```json
{
  "mcp": {
    "servers": {
      "eloverblik": {
        "type": "stdio",
        "command": "uv",
        "args": [
          "--directory",
          "C:\\Users\\<user>\\path\\to\\eloverblik_api_mcp",
          "run",
          "main.py"
        ]
      }
    }
  }
}
```

**macOS/Linux**:
```json
{
  "mcp": {
    "servers": {
      "eloverblik": {
        "type": "stdio",
        "command": "uv",
        "args": [
          "--directory",
          "/home/<user>/path/to/eloverblik_api_mcp",
          "run",
          "main.py"
        ]
      }
    }
  }
}
```

Replace `<user>` and adjust the path to match your installation directory.


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

Example:
```
Show me all metering points and their current charges.
Export my hourly timeseries for 2024-01-01 to 2024-01-31.
```

### Example Prompts

After setting up the MCP server with your AI client:

- *"Check if the Eloverblik API is working"*
- *"Get my access token and list all metering points"*
- *"Add relation for metering point X with web access code Y"*
- *"Show me charges and details for all my configured metering points"*
- *"Export hourly consumption data for January 2024 as CSV"*

### Legacy Examples

The core tools remain available with backward-compatible behavior:

- **eloverblik_isalive**
   ```
   Test the Eloverblik API connection
   ```

- **eloverblik_metering_points**
   ```
   Show me my electricity metering points
   ```

- **eloverblik_timeseries**
   ```
   Show my electricity consumption for January 2024 by day
   Get hourly consumption data from 2024-03-01 to 2024-03-31
   ```

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
eloverblik_api_mcp/
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