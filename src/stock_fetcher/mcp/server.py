import os
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    print("Error: MCP server dependencies are missing.", file=sys.stderr)
    print("Install via: pip install 'stock-fetcher[mcp]'", file=sys.stderr)
    sys.exit(1)

from ..exceptions import ProviderNotFoundError, StockFetcherError
from ..factory import ClientFactory

mcp = FastMCP("stock_fetcher")


@mcp.tool()
def search_images(
    provider: str,
    term: str,
    limit: int = 5,
    page: int = 1,
    cursor: str = "",
    api_key: str = "",
) -> str:
    """Search for copyright-free images using a specified provider.

    Args:
        provider: The image provider ('pixabay', 'pexels', 'unsplash', 'flickr', 'wikimedia', 'openverse').
        term: Search query string (e.g. 'nature', 'city').
        limit: Maximum number of images to return (bounded between 1 and 30).
        page: Page number for deterministic pagination (1-indexed).
        cursor: Optional opaque deterministic cursor string.
        api_key: The API key for the provider. If omitted, attempts to read from env vars.
    """
    clean_provider = provider.strip().lower()
    clean_term = term.strip()

    if not clean_term:
        return "Error: Search term cannot be empty."

    safe_limit = max(1, min(int(limit), 30))

    if not api_key:
        env_var_name = f"{clean_provider.upper()}_API_KEY"
        api_key = os.getenv(env_var_name, "")

    try:
        client = ClientFactory.get(clean_provider, api_key=api_key)
        images = client.search(
            clean_term,
            limit=safe_limit,
            page=page,
            cursor=cursor if cursor else None,
        )

        if not images:
            return f"No images found for '{clean_term}' on {clean_provider}."

        result = (
            f"Found {len(images)} images for '{clean_term}' on {clean_provider}:\n\n"
        )
        for img in images:
            img_id = img.get("id", "N/A")
            img_url = img.get("url_original") or img.get("url") or "N/A"
            result += f"- [{img_id}] {img_url}\n"

        return result

    except ProviderNotFoundError as e:
        return f"Provider error: {e}"
    except StockFetcherError as e:
        # Avoid leaking raw credentials in error responses
        clean_msg = str(e)
        if api_key and api_key in clean_msg:
            clean_msg = clean_msg.replace(api_key, "***")
        return f"Error fetching images: {clean_msg}"


if __name__ == "__main__":
    mcp.run()
