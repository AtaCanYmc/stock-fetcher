from abc import ABC, abstractmethod
from typing import List, Any


class BaseFetcher(ABC):
    """
    Abstract base class for all image fetcher clients.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    @abstractmethod
    def search(self, term: str, limit: int) -> List[Any]:
        """
        Search for images based on a search term.

        Args:
            term (str): The search term.
            limit (int): Maximum number of images to return.

        Returns:
            List[Any]: A list of fetched images (can be dicts or Pydantic models).
        """
        pass
