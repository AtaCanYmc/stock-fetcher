import requests
from typing import List, Any
from ..base import BaseFetcher
from ..exceptions import APIConnectionError, AuthenticationError


class UnsplashClient(BaseFetcher):
    """Client for fetching copyright-free images from Unsplash."""

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://api.unsplash.com"

    def search(self, term: str, limit: int = 15) -> List[Any]:
        if not self.api_key:
            raise AuthenticationError("Unsplash requires an API key (client_id).")

        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=30)

        url = f"{self.base_url}/search/photos"
        params = {
            "query": clean_term,
            "per_page": safe_limit,
            "client_id": self.api_key,
            "order_by": "relevant",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed with status code {response.status_code}."
                )
            response.raise_for_status()

            data = response.json()
            results = []
            for item in data.get("results", []):
                links_dict = item.get("links", {})
                urls_dict = item.get("urls", {})
                results.append(
                    {
                        "id": str(item.get("id", "")),
                        "source": "unsplash",
                        "url": links_dict.get("html", ""),
                        "url_original": urls_dict.get("raw", ""),
                    }
                )
            return results
        except requests.RequestException as e:
            err_msg = str(e)
            if self.api_key and self.api_key in err_msg:
                err_msg = err_msg.replace(self.api_key, "***")
            raise APIConnectionError(f"Failed to fetch from Unsplash: {err_msg}")
