import requests
from typing import List, Any
from ..base import BaseFetcher
from ..exceptions import APIConnectionError, AuthenticationError


class PexelsClient(BaseFetcher):
    """Client for fetching copyright-free images from Pexels."""

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://api.pexels.com/v1"

    def search(self, term: str, limit: int = 15) -> List[Any]:
        if not self.api_key:
            raise AuthenticationError("Pexels requires an API key.")

        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=80)

        url = f"{self.base_url}/search"
        headers = {"Authorization": self.api_key}
        params = {"query": clean_term, "per_page": safe_limit}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed with status code {response.status_code}."
                )
            response.raise_for_status()

            data = response.json()
            results = []
            for item in data.get("photos", []):
                src_dict = item.get("src", {})
                results.append(
                    {
                        "id": str(item.get("id", "")),
                        "source": "pexels",
                        "url": item.get("url", ""),
                        "url_original": src_dict.get("original", ""),
                    }
                )
            return results
        except requests.RequestException as e:
            err_msg = str(e)
            if self.api_key and self.api_key in err_msg:
                err_msg = err_msg.replace(self.api_key, "***")
            raise APIConnectionError(f"Failed to fetch from Pexels: {err_msg}")
