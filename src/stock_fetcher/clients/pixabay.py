import requests
from typing import List, Any
from ..base import BaseFetcher
from ..exceptions import APIConnectionError, AuthenticationError


class PixabayClient(BaseFetcher):
    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://pixabay.com/api/"

    def search(self, term: str, limit: int = 15) -> List[Any]:
        if not self.api_key:
            raise AuthenticationError("Pixabay requires an API key.")

        params = {
            "key": self.api_key,
            "q": term,
            "per_page": limit,
            "image_type": "photo",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed: {response.status_code}"
                )
            response.raise_for_status()

            data = response.json()
            if "error" in data:
                raise APIConnectionError(f"Pixabay API error: {data['error']}")

            results = []
            for item in data.get("hits", []):
                results.append(
                    {
                        "id": str(item["id"]),
                        "source": "pixabay",
                        "url": item["pageURL"],
                        "url_original": item["largeImageURL"],
                    }
                )
            return results
        except requests.RequestException as e:
            raise APIConnectionError(f"Failed to fetch from Pixabay: {e}")
