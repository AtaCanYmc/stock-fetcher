import requests
from typing import List, Any
from ..base import BaseFetcher
from ..exceptions import APIConnectionError, AuthenticationError


class PixabayClient(BaseFetcher):
    """Client for fetching copyright-free images from Pixabay."""

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://pixabay.com/api/"

    def search(self, term: str, limit: int = 15) -> List[Any]:
        if not self.api_key:
            raise AuthenticationError("Pixabay requires an API key.")

        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=100)

        params = {
            "key": self.api_key,
            "q": clean_term,
            "per_page": safe_limit,
            "image_type": "photo",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed with status code {response.status_code}."
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
                        "url": item.get("pageURL", ""),
                        "url_original": item.get("largeImageURL", ""),
                    }
                )
            return results
        except requests.RequestException as e:
            # Mask API key if present in request URL within exception string
            err_msg = str(e)
            if self.api_key and self.api_key in err_msg:
                err_msg = err_msg.replace(self.api_key, "***")
            raise APIConnectionError(f"Failed to fetch from Pixabay: {err_msg}")
