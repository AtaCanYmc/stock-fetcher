from typing import Optional


class StockFetcherError(Exception):
    """Base exception class for all errors in stock-fetcher."""

    pass


class APIConnectionError(StockFetcherError):
    """Raised when there is an issue connecting to the API."""

    pass


class RateLimitExceededError(APIConnectionError):
    """Raised when an API rate limit is hit and retries are exhausted."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        provider: str = "",
    ):
        super().__init__(message)
        self.retry_after = retry_after
        self.provider = provider


class AuthenticationError(StockFetcherError):
    """Raised when authentication fails (e.g. invalid API key)."""

    pass


class ProviderNotFoundError(StockFetcherError):
    """Raised when an unsupported provider is requested."""

    pass
