import sys
import os

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    print("HATA: MCP sunucu özellikleri için gerekli kütüphaneler eksik.")
    print("Bu özelliği kullanmak için lütfen aşağıdaki komutu çalıştırın:")
    print("    pip install 'stock-fetcher[mcp]'")
    sys.exit(1)

from ..factory import ClientFactory
from ..exceptions import StockFetcherError

mcp = FastMCP("stock_fetcher")


@mcp.tool()
def search_images(provider: str, term: str, limit: int = 5, api_key: str = "") -> str:
    """
    Search for copyright-free images using a specified provider.

    Args:
        provider: The image provider (e.g., 'pixabay', 'pexels').
        term: The search term (e.g., 'nature', 'cats').
        limit: Maximum number of images to return (default: 5).
        api_key: The API key for the provider. If omitted, attempts to use env vars.
    """
    if not api_key:
        env_var_name = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_var_name, "")

    try:
        client = ClientFactory.get(provider, api_key=api_key)
        images = client.search(term, limit=limit)

        if not images:
            return f"No images found for '{term}' on {provider}."

        result = f"Found {len(images)} images for '{term}' on {provider}:\n\n"
        for img in images:
            result += f"- [{img.get('id', 'N/A')}] {img.get('url', 'N/A')}\n"

        return result

    except StockFetcherError as e:
        return f"Error fetching images: {e}"


if __name__ == "__main__":
    mcp.run()
