# Eloverblik API MCP

## Overview
This project provides a Model Context Protocol (MCP) server for interacting with the Eloverblik API. It allows users to fetch and analyze energy consumption data from the Danish energy grid.

## Features
- Fetch metering point details.
- Retrieve time series data for energy consumption.
- Automatically fetch and refresh API access tokens.
- Analyze energy usage patterns.

## Requirements
- Python 3.8+
- An active Eloverblik API refresh token.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd eloverblik_api_mcp
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. Create a `.env` file in the project root with the following variables:
   ```env
   API_REFRESH_TOKEN=<your_api_refresh_token>
   METERING_POINT_ID=<your_metering_point_id>
   ```

## confiugre MCP server in Visual Studio Ccode
1. Open Visual Studio Code and navigate to the settings file. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open Settings (JSON)`.

2. Add the following configuration to your settings file, replacing `<user>` with your actual username and ensuring the paths are correct for your system:

```json
C:\Users\<user>\AppData\Roaming\Code\User\settings.json

    "mcp": {
        "servers": {
            "eloverblik mcp": {
                "type": "stdio",
                "command": "c:\\Users\\<user>\\Desktop\\eloverblik_api_mcp\\.venv\\Scripts\\python.exe",
                "args": [
                    "c:\\Users\\<user>\\Desktop\\eloverblik_api_mcp\\main.py"
                ],
            }
        }
    }
```


## Usage
1. Set up your Eloverblik API token & metering point ID in the `.env` file

2. Run the MCP server in VSC:
- F1 -> MCP: List servers -> eloverblik mcp -> Enter
3. Now prompt the chatGPT agent, ie: `#eloverblik_timeseries tell me about my consumption for April 2025`

## Debugging during development
1. Run the MCP server:
   ```bash
   uv run python main.py
   ```