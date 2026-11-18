import asyncio
import os

from stock_fetcher import ClientFactory, MemoryCache, StockImage


async def main():
    print("=== Stock Fetcher v0.3.0 Async & Caching Demo ===")

    # 1. Configurable In-Memory or Disk Caching
    cache = MemoryCache(default_ttl=1800)  # 30 minutes TTL

    # 2. Asynchronous Query to a Single Provider
    print("\n[1] Asynchronous Query to Flickr (Zero Config)")
    flickr = ClientFactory.get("flickr", cache=cache)
    images = await flickr.asearch("classic vintage cars", limit=3)

    for img in images:
        # Access via structured Pydantic attributes or dict subscript
        print(f"[{img.source.upper()}] ID: {img.id}")
        print(f"  Title:    {img.title}")
        print(f"  Original: {img.url_original}\n")

    # 3. Concurrent Multi-Provider Fetching via asyncio.gather
    print("[2] Concurrent Multi-Provider Search (Pixabay + Flickr)")
    keys = {
        "pixabay": os.getenv("PIXABAY_API_KEY", ""),
        "pexels": os.getenv("PEXELS_API_KEY", ""),
        "unsplash": os.getenv("UNSPLASH_API_KEY", ""),
    }

    # Query all available/configured providers concurrently in parallel
    results_map = await ClientFactory.asearch_all(
        term="northern lights aurora",
        limit=2,
        api_keys=keys,
        cache=cache,
        providers=["flickr", "pixabay"],
    )

    for provider_name, provider_images in results_map.items():
        print(
            f"\n--- Provider: {provider_name.capitalize()} ({len(provider_images)} results) ---"
        )
        for pic in provider_images:
            assert isinstance(pic, StockImage)
            print(f"  - [{pic.id}] {pic.url_page} -> {pic.url_original}")


if __name__ == "__main__":
    asyncio.run(main())
