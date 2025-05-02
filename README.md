# Eloverblik API MCP

## Overview
This project provides a Model Context Protocol (MCP) server for interacting with the Eloverblik API. It allows users to fetch and analyze energy consumption data from the Danish energy grid.

## Features
- Fetch metering point details.
- Retrieve time series data for energy consumption.
- Analyze energy usage patterns.

## Requirements
- Python 3.8+
- uv
- An active Eloverblik API token.

## Installation & activation
uv sync
source .venv/scripts/activate

## confiugre MCP serverf in VSC
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


## Usage
1. Set up your Eloverblik API token & metering point ID in the `.env` file

2. Run the MCP server in VSC:
- F1 -> MCP: List servers -> eloverblik mcp -> Enter
3. Now prompt the chatGPT agent, ie: `#eloverblik_timeseries tell me about my consumption for April 2025`
