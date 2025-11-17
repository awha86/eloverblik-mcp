# Eloverblik API MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for interacting with the Danish [Eloverblik API](https://api.eloverblik.dk/), built with [FastMCP](https://github.com/jlowin/fastmcp).

## Overview

This MCP server provides tools to access electricity consumption data from the Danish national energy grid through the Eloverblik API. It enables AI assistants to fetch and analyze your energy usage patterns.

## Features

- 🔌 **Check API Status** - Verify Eloverblik API connectivity
- 📊 **Metering Points** - Fetch details about your electricity metering points
- 📈 **Time Series Data** - Retrieve consumption data with multiple aggregation levels (actual, hour, day, month, year)
- 🔐 **Automatic Authentication** - Handles API token management automatically
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

### Available Tools

1. **eloverblik_isalive** - Check API connectivity
   ```
   Test the Eloverblik API connection
   ```

2. **eloverblik_metering_points** - List your metering points
   ```
   Show me my electricity metering points
   ```

3. **eloverblik_timeseries** - Get consumption data
   ```
   Show my electricity consumption for January 2024 by day
   Get hourly consumption data from 2024-03-01 to 2024-03-31
   ```

### Example Prompts

After setting up the MCP server with your AI client:

- *"Check if the Eloverblik API is working"*
- *"Show me all my metering points"*
- *"What was my electricity consumption last month?"*
- *"Get my daily energy usage for April 2024"*
- *"Show hourly consumption data for the first week of March 2024"*

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