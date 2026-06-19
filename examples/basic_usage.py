import os
from stock_fetcher import ClientFactory


def main():
    print("=== Stock Fetcher Basic Usage ===")

    # 1. Pixabay Example (Requires API Key)
    print("\n--- Pixabay Example ---")
    pixabay_key = os.getenv("PIXABAY_API_KEY", "YOUR_PIXABAY_API_KEY")
    try:
        pixabay = ClientFactory.get("pixabay", api_key=pixabay_key)
        images = pixabay.search("mountains", limit=2)

        for img in images:
            print(f"[{img['source']}] ID: {img['id']} -> {img['url_original']}")
    except Exception as e:
        print(f"Failed to fetch from Pixabay (did you set your API key?): {e}")

    # 2. Flickr Example (No API Key required, uses scraping)
    print("\n--- Flickr Example ---")
    try:
        flickr = ClientFactory.get("flickr")
        images = flickr.search("vintage cars", limit=2)

        for img in images:
            print(f"[{img['source']}] ID: {img['id']} -> {img['url_original']}")
    except Exception as e:
        print(f"Failed to fetch from Flickr: {e}")

    # 3. Pexels Example (Requires API Key)
    print("\n--- Pexels Example ---")
    pexels_key = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY")
    try:
        pexels = ClientFactory.get("pexels", api_key=pexels_key)
        images = pexels.search("technology", limit=2)

        for img in images:
            print(f"[{img['source']}] ID: {img['id']} -> {img['url_original']}")
    except Exception as e:
        print(f"Failed to fetch from Pexels (did you set your API key?): {e}")

    # 4. Unsplash Example (Requires API Key / Client ID)
    print("\n--- Unsplash Example ---")
    unsplash_key = os.getenv("UNSPLASH_API_KEY", "YOUR_UNSPLASH_API_KEY")
    try:
        unsplash = ClientFactory.get("unsplash", api_key=unsplash_key)
        images = unsplash.search("architecture", limit=2)

        for img in images:
            print(f"[{img['source']}] ID: {img['id']} -> {img['url_original']}")
    except Exception as e:
        print(f"Failed to fetch from Unsplash (did you set your API key?): {e}")


if __name__ == "__main__":
    main()
