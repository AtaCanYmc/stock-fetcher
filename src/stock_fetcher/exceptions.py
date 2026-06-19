class StockFetcherError(Exception):
    """Base exception class for all errors in stock-fetcher."""

    pass


class APIConnectionError(StockFetcherError):
    """Raised when there is an issue connecting to the API."""

    pass


class AuthenticationError(StockFetcherError):
    """Raised when authentication fails (e.g. invalid API key)."""

    pass


class ProviderNotFoundError(StockFetcherError):
    """Raised when an unsupported provider is requested."""

    pass
