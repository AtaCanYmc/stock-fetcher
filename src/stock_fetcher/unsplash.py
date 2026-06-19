import requests
from typing import List, Dict, Any
from .base import BaseFetcher
from .exceptions import FetcherError

class UnsplashClient(BaseFetcher):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.unsplash.com"

    def search_images(self, query: str, per_page: int = 15, page: int = 1) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "client_id": self.api_key,
            "order_by": "relevant"
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append({
                    "id": str(item["id"]),
                    "source": "unsplash",
                    "url": item["links"]["html"],
                    "url_original": item["urls"]["raw"],
                    "url_thumbnail": item["urls"]["thumb"],
                    "width": item["width"],
                    "height": item["height"],
                    "photographer": item["user"]["username"],
                    "description": item.get("description") or item.get("alt_description")
                })
            return results
        except requests.RequestException as e:
            raise FetcherError(f"Failed to fetch images from Unsplash: {e}")

    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/photos/{image_id}"
        params = {
            "client_id": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            item = response.json()
            
            return {
                "id": str(item["id"]),
                "source": "unsplash",
                "url": item["links"]["html"],
                "url_original": item["urls"]["raw"],
                "url_thumbnail": item["urls"]["thumb"],
                "width": item["width"],
                "height": item["height"],
                "photographer": item["user"]["username"],
                "description": item.get("description") or item.get("alt_description")
            }
        except requests.RequestException as e:
            raise FetcherError(f"Failed to fetch image details from Unsplash: {e}")
