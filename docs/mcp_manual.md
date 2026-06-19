# Stock Fetcher MCP Manual

The Model Context Protocol (MCP) server allows AI agents (like Claude Desktop) to use Stock Fetcher as an external tool to search for images on your behalf.

## Installation

Ensure you install the package with the `mcp` extra:

```bash
pip install 'stock-fetcher[mcp]'
```

## How It Works

MCP uses standard input/output (stdio) to communicate. The `mcp_server.py` module exposes a single tool called `search_images`. When an AI agent needs to find a picture, it sends a JSON-RPC request to this server, which executes the search using the specified provider and returns the image URLs back to the AI.

## Claude Desktop Configuration

To integrate this tool with Claude Desktop, you need to add it to your configuration file.

### Location of `claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration Snippet

Add the following configuration block to the file:

```json
{
  "mcpServers": {
    "stock_fetcher": {
      "command": "python",
      "args": ["-m", "stock_fetcher.mcp.server"],
      "env": {
        "PEXELS_API_KEY": "your_pexels_key_here",
        "PIXABAY_API_KEY": "your_pixabay_key_here",
        "UNSPLASH_API_KEY": "your_unsplash_key_here"
      }
    }
  }
}
```

*Make sure your Python path in the `command` variable is accessible by Claude, or provide the absolute path to your `.venv/bin/python` if you are using a virtual environment.*

Once configured, restart Claude Desktop. You can now ask Claude questions like:
> *"Find me 3 pictures of a futuristic city using Pixabay."*

## Antigravity Configuration

Antigravity natively supports connecting to external MCP tools. To use Stock Fetcher as a tool within Antigravity, add the server configuration to your Antigravity MCP settings file (typically formatted the same way):

```json
{
  "mcpServers": {
    "stock_fetcher": {
      "command": "python",
      "args": ["-m", "stock_fetcher.mcp.server"],
      "env": {
        "PEXELS_API_KEY": "your_pexels_key_here",
        "PIXABAY_API_KEY": "your_pixabay_key_here",
        "UNSPLASH_API_KEY": "your_unsplash_key_here"
      }
    }
  }
}
```

Once configured, Antigravity will automatically discover the `search_images` tool. You can simply ask Antigravity:
> *"Pixabay üzerinden bana 2 tane doğa manzarası bulup linklerini verir misin?"*

## Running the Server Manually

While the MCP server is designed to be run by a client application, you can start the process manually:

```bash
python -m stock_fetcher.mcp.server
```
The server will silently wait for valid JSON-RPC messages on `stdin`.
