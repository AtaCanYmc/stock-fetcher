from stock_fetcher import ClientFactory
from stock_fetcher import StockFetcherError, AuthenticationError, ProviderNotFoundError


def main():
    print("=== Stock Fetcher Error Handling ===")

    # 1. Provider Not Found Error
    print("\n--- Testing Invalid Provider ---")
    try:
        client = ClientFactory.get("invalid_provider")
    except ProviderNotFoundError as e:
        print(f"Caught Expected Error: {e}")

    # 2. Authentication Error
    print("\n--- Testing Invalid API Key ---")
    try:
        # Pexels requires a valid API key
        client = ClientFactory.get("pexels", api_key="INVALID_KEY_123")
        client.search("technology", limit=1)
    except AuthenticationError as e:
        print(f"Caught Expected Authentication Error: {e}")
    except StockFetcherError as e:
        print(f"Caught generic fetcher error: {e}")


if __name__ == "__main__":
    main()
