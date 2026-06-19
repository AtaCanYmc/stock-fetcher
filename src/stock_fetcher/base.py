from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseFetcher(ABC):
    """
    Abstract base class for all image fetcher clients.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = ""

    @abstractmethod
    def search_images(self, query: str, per_page: int = 15, page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for images based on a query.

        Args:
            query (str): The search term.
            per_page (int): Number of results per page.
            page (int): Page number.

        Returns:
            List[Dict[str, Any]]: A list of image dictionaries containing at least 'url', 'id', and 'source'.
            
        Raises:
            FetcherError: If there is an issue with the API request.
        """
        pass

    @abstractmethod
    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        """
        Get details for a specific image.

        Args:
            image_id (str): The unique identifier for the image.

        Returns:
            Dict[str, Any]: Image details.
            
        Raises:
            FetcherError: If there is an issue fetching the details.
        """
        pass
