import requests
from typing import List, Any
from ..base import BaseFetcher
from ..exceptions import APIConnectionError, AuthenticationError


class UnsplashClient(BaseFetcher):
    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://api.unsplash.com"

    def search(self, term: str, limit: int = 15) -> List[Any]:
        if not self.api_key:
            raise AuthenticationError("Unsplash requires an API key (client_id).")

        url = f"{self.base_url}/search/photos"
        params = {
            "query": term,
            "per_page": limit,
            "client_id": self.api_key,
            "order_by": "relevant",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed: {response.status_code}"
                )
            response.raise_for_status()

            data = response.json()
            results = []
            for item in data.get("results", []):
                results.append(
                    {
                        "id": str(item["id"]),
                        "source": "unsplash",
                        "url": item["links"]["html"],
                        "url_original": item["urls"]["raw"],
                    }
                )
            return results
        except requests.RequestException as e:
            raise APIConnectionError(f"Failed to fetch from Unsplash: {e}")
