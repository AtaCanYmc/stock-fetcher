from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from .cache import BaseCache, build_cache_key, parse_cache_control_ttl
from .models import StockImage


class BaseFetcher(ABC):
    """Abstract base class for all image fetcher clients."""

    def __init__(self, api_key: str = "", cache: Optional[BaseCache] = None):
        self.api_key = api_key.strip() if api_key else ""
        self.cache = cache

    @property
    @abstractmethod
    def name(self) -> str:
        """Normalized lowercase provider name."""
        pass

    @staticmethod
    def sanitize_search_params(
        term: str, limit: int, max_limit: int = 100
    ) -> Tuple[str, int]:
        """Validate search query and enforce safe pagination bounds.

        Args:
            term: The search query string.
            limit: Requested number of items.
            max_limit: Upper bound ceiling to prevent rate limit abuse.

        Returns:
            Tuple[str, int]: Cleaned term and clamped limit.

        Raises:
            ValueError: If term is empty or invalid.
        """
        if not isinstance(term, str) or not term.strip():
            raise ValueError("Search term cannot be empty.")

        clean_term = term.strip()
        try:
            clamped_limit = max(1, min(int(limit), max_limit))
        except (TypeError, ValueError):
            clamped_limit = 15

        return clean_term, clamped_limit

    def _get_cached_results(self, term: str, limit: int) -> Optional[List[StockImage]]:
        """Retrieve cached results if cache is configured and entry is unexpired."""
        if not self.cache:
            return None
        key = build_cache_key(self.name, term, limit)
        cached_data = self.cache.get(key)
        if cached_data is not None:
            return [StockImage(**item) for item in cached_data]
        return None

    def _save_cached_results(
        self,
        term: str,
        limit: int,
        results: List[StockImage],
        headers: Any = None,
    ) -> None:
        """Store results into cache honoring upstream Cache-Control headers."""
        if not self.cache:
            return
        key = build_cache_key(self.name, term, limit)
        ttl = parse_cache_control_ttl(headers)
        data = [img.to_dict() for img in results]
        self.cache.set(key, data, ttl=ttl)

    @abstractmethod
    def search(self, term: str, limit: int = 15) -> List[StockImage]:
        """Synchronous search for images based on a search term.

        Args:
            term: The search term.
            limit: Maximum number of images to return.

        Returns:
            List[StockImage]: List of fetched image models.
        """
        pass

    @abstractmethod
    async def asearch(self, term: str, limit: int = 15) -> List[StockImage]:
        """Asynchronous non-blocking search for images using httpx.

        Args:
            term: The search term.
            limit: Maximum number of images to return.

        Returns:
            List[StockImage]: List of fetched image models.
        """
        pass
