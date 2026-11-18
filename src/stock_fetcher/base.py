from abc import ABC, abstractmethod
from typing import List, Any, Tuple


class BaseFetcher(ABC):
    """Abstract base class for all image fetcher clients."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip() if api_key else ""

    @staticmethod
    def sanitize_search_params(term: str, limit: int, max_limit: int = 100) -> Tuple[str, int]:
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

    @abstractmethod
    def search(self, term: str, limit: int = 15) -> List[Any]:
        """Search for images based on a search term.

        Args:
            term: The search term.
            limit: Maximum number of images to return.

        Returns:
            List[Any]: List of fetched image dictionaries.
        """
        pass
