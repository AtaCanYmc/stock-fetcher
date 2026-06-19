import requests
from typing import List, Dict, Any
from .base import BaseFetcher
from .exceptions import FetcherError

class PixabayClient(BaseFetcher):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://pixabay.com/api/"

    def search_images(self, query: str, per_page: int = 15, page: int = 1) -> List[Dict[str, Any]]:
        params = {
            "key": self.api_key,
            "q": query,
            "page": page,
            "per_page": per_page,
            "image_type": "photo"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise FetcherError(f"Pixabay API error: {data['error']}")
                
            results = []
            for item in data.get("hits", []):
                results.append({
                    "id": str(item["id"]),
                    "source": "pixabay",
                    "url": item["pageURL"],
                    "url_original": item["largeImageURL"],
                    "url_thumbnail": item["previewURL"],
                    "width": item["imageWidth"],
                    "height": item["imageHeight"],
                    "photographer": item["user"]
                })
            return results
        except requests.RequestException as e:
            raise FetcherError(f"Failed to fetch images from Pixabay: {e}")

    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        params = {
            "key": self.api_key,
            "id": image_id
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise FetcherError(f"Pixabay API error: {data['error']}")
                
            hits = data.get("hits", [])
            if not hits:
                raise FetcherError(f"Image {image_id} not found on Pixabay")
                
            item = hits[0]
            return {
                "id": str(item["id"]),
                "source": "pixabay",
                "url": item["pageURL"],
                "url_original": item["largeImageURL"],
                "url_thumbnail": item["previewURL"],
                "width": item["imageWidth"],
                "height": item["imageHeight"],
                "photographer": item["user"]
            }
        except requests.RequestException as e:
            raise FetcherError(f"Failed to fetch image details from Pixabay: {e}")
