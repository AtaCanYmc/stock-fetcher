import requests
from typing import List, Any
from ..base import BaseFetcher
from ..exceptions import APIConnectionError, AuthenticationError


class PexelsClient(BaseFetcher):
    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://api.pexels.com/v1"

    def search(self, term: str, limit: int = 15) -> List[Any]:
        if not self.api_key:
            raise AuthenticationError("Pexels requires an API key.")

        url = f"{self.base_url}/search"
        headers = {"Authorization": self.api_key}
        params = {"query": term, "per_page": limit}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed: {response.status_code}"
                )
            response.raise_for_status()

            data = response.json()
            results = []
            for item in data.get("photos", []):
                results.append(
                    {
                        "id": str(item["id"]),
                        "source": "pexels",
                        "url": item["url"],
                        "url_original": item["src"]["original"],
                    }
                )
            return results
        except requests.RequestException as e:
            raise APIConnectionError(f"Failed to fetch from Pexels: {e}")
