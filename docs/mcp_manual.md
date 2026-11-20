[← Back to Root Repository](../README.md) | [CLI Manual](cli_manual.md) | [API Keys Guide](api_keys_guide.md)

# stock-fetcher MCP Manual

The Model Context Protocol (MCP) server enables AI agents to query `stock-fetcher` tools over standard input/output (stdio) streams.

---

## Table of Contents

- [Installation](#installation)
- [Protocol Specification](#protocol-specification)
- [Tool Definitions](#tool-definitions)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Google Antigravity Integration](#google-antigravity-integration)
- [Manual Server Execution](#manual-server-execution)

---

## Installation

Install the package with the `mcp` optional extra:

```bash
pip install "stock-fetcher[mcp]"
```

---

## Protocol Specification

The server runs as an independent child process communicating via stdio JSON-RPC messages. Host agents dispatch structured tool calls and receive JSON image arrays containing `id`, `source`, `url_original`, `url_thumb`, and `url_page`.

---

## Tool Definitions

The server registers one primary tool:

### `search_images`

Searches for copyright-free images using the specified provider.

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `term` | String | Yes | None | Image search query. |
| `provider` | String | No | `"pixabay"` | Provider name: `pixabay`, `pexels`, `unsplash`, `flickr`, `wikimedia`, `openverse`. |
| `limit` | Integer | No | `5` | Maximum number of results to return (clamped 1&ndash;30). |
| `page` | Integer | No | `1` | 1-indexed page number for deterministic pagination. |
| `cursor` | String | No | `""` | Optional opaque deterministic cursor string. |
| `api_key` | String | No | `""` | Explicit provider token (overrides environment variables). |

---

## Claude Desktop Integration

Locate your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the server definition under `mcpServers`:

```json
{
  "mcpServers": {
    "stock_fetcher": {
      "command": "python",
      "args": ["-m", "stock_fetcher.mcp.server"],
      "env": {
        "PEXELS_API_KEY": "YOUR_PEXELS_KEY",
        "PIXABAY_API_KEY": "YOUR_PIXABAY_KEY",
        "UNSPLASH_API_KEY": "YOUR_UNSPLASH_KEY"
      }
    }
  }
}
```

Restart Claude Desktop to activate tool registration.

---

## Google Antigravity Integration

Add the server block to your Antigravity MCP settings:

```json
{
  "mcpServers": {
    "stock_fetcher": {
      "command": "python",
      "args": ["-m", "stock_fetcher.mcp.server"],
      "env": {
        "PEXELS_API_KEY": "YOUR_PEXELS_KEY",
        "PIXABAY_API_KEY": "YOUR_PIXABAY_KEY",
        "UNSPLASH_API_KEY": "YOUR_UNSPLASH_KEY"
      }
    }
  }
}
```

---

## Manual Server Execution

You can run the MCP server standalone to verify stdio initialization:

```bash
python -m stock_fetcher.mcp.server
```

The process will start and wait for standard JSON-RPC initialization payloads on `stdin`.
