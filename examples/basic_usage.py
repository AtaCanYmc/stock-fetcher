import os
from stock_fetcher import ClientFactory


def main():
    print("=== Stock Fetcher Basic Usage ===")

    # 1. Pixabay Example (Requires API Key)
    print("\n--- Pixabay Example ---")
    pixabay_key = os.getenv("PIXABAY_API_KEY", "YOUR_PIXABAY_API_KEY")

    try:
        pixabay = ClientFactory.get("pixabay", api_key=pixabay_key)
        images = pixabay.search("mountains", limit=3)

        for img in images:
            print(f"[{img['source']}] ID: {img['id']} -> {img['url_original']}")
    except Exception as e:
        print(f"Failed to fetch from Pixabay (did you set your API key?): {e}")

    # 2. Flickr Example (No API Key required, uses scraping)
    print("\n--- Flickr Example ---")
    try:
        flickr = ClientFactory.get("flickr")
        images = flickr.search("vintage cars", limit=3)

        for img in images:
            print(f"[{img['source']}] ID: {img['id']} -> {img['url_original']}")
    except Exception as e:
        print(f"Failed to fetch from Flickr: {e}")


if __name__ == "__main__":
    main()
