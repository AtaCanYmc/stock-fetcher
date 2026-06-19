import requests
from typing import List, Dict, Any
from .base import BaseFetcher
from .exceptions import FetcherError

class PexelsClient(BaseFetcher):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": self.api_key}

    def search_images(self, query: str, per_page: int = 15, page: int = 1) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "per_page": per_page,
            "page": page
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("photos", []):
                results.append({
                    "id": str(item["id"]),
                    "source": "pexels",
                    "url": item["url"],
                    "url_original": item["src"]["original"],
                    "url_thumbnail": item["src"]["tiny"],
                    "width": item["width"],
                    "height": item["height"],
                    "photographer": item["photographer"]
                })
            return results
        except requests.RequestException as e:
            raise FetcherError(f"Failed to fetch images from Pexels: {e}")

    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/photos/{image_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            item = response.json()
            
            return {
                "id": str(item["id"]),
                "source": "pexels",
                "url": item["url"],
                "url_original": item["src"]["original"],
                "url_thumbnail": item["src"]["tiny"],
                "width": item["width"],
                "height": item["height"],
                "photographer": item["photographer"]
            }
        except requests.RequestException as e:
            raise FetcherError(f"Failed to fetch image details from Pexels: {e}")
