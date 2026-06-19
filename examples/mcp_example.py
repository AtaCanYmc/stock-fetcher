"""
============================================================================
Stock Fetcher MCP Server Usage Example

Make sure you have installed the MCP extras:
pip install -e ".[mcp]"
============================================================================

The Model Context Protocol (MCP) server is designed to be run as a background
process and communicate with an AI agent (like Claude Desktop) via standard
input/output (stdio).

How to use the MCP Server:

1. STANDALONE RUN:
   You can start the server manually by running:
   python -m stock_fetcher.mcp.server

   (It will wait for JSON-RPC messages over stdin).

2. CLAUDE DESKTOP CONFIGURATION:
   To let Claude Desktop use your Stock Fetcher tool, add this to your
   `claude_desktop_config.json`:

   {
     "mcpServers": {
       "stock_fetcher": {
         "command": "python",
         "args": ["-m", "stock_fetcher.mcp.server"],
         "env": {
            "PIXABAY_API_KEY": "your_api_key_here"
         }
       }
     }
   }

3. TESTING WITH MCP INSPECTOR:
   If you have the MCP CLI installed, you can inspect the tools interactively:
   npx @modelcontextprotocol/inspector python -m stock_fetcher.mcp.server
"""

if __name__ == "__main__":
    print("This file is a documentation example.")
    print(
        "Please read the source code of this file to see how to configure and run the MCP Server."
    )
