from typing import List, Dict, Any, Optional
import httpx
from ..base import BaseFetcher
from ..models import StockImage
from ..cache import BaseCache
from ..exceptions import APIConnectionError, AuthenticationError


class PexelsClient(BaseFetcher):
    """Client for fetching copyright-free images from Pexels."""

    def __init__(self, api_key: str = "", cache: Optional[BaseCache] = None):
        super().__init__(api_key=api_key, cache=cache)
        self.base_url = "https://api.pexels.com/v1"

    @property
    def name(self) -> str:
        return "pexels"

    def _parse_payload(self, data: Dict[str, Any]) -> List[StockImage]:
        results: List[StockImage] = []
        for item in data.get("photos", []):
            src_dict = item.get("src", {})
            results.append(
                StockImage(
                    id=str(item.get("id", "")),
                    source="pexels",
                    url_page=item.get("url", ""),
                    url_original=src_dict.get("original", ""),
                    url_thumb=src_dict.get("tiny") or src_dict.get("small"),
                    title=item.get("alt") or "",
                    author=item.get("photographer", ""),
                    width=item.get("width"),
                    height=item.get("height"),
                    extra={
                        "photographer_url": item.get("photographer_url"),
                        "avg_color": item.get("avg_color"),
                    },
                )
            )
        return results

    def _mask_error(self, exc: Exception) -> str:
        err_msg = str(exc)
        if self.api_key and self.api_key in err_msg:
            err_msg = err_msg.replace(self.api_key, "***")
        return err_msg

    def search(self, term: str, limit: int = 15) -> List[StockImage]:
        if not self.api_key:
            raise AuthenticationError("Pexels requires an API key.")

        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=80)
        cached = self._get_cached_results(clean_term, safe_limit)
        if cached is not None:
            return cached

        url = f"{self.base_url}/search"
        headers = {"Authorization": self.api_key}
        params = {"query": clean_term, "per_page": safe_limit}

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=headers, params=params)
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(clean_term, safe_limit, images, response.headers)
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(f"Failed to fetch from Pexels: {self._mask_error(e)}")

    async def asearch(self, term: str, limit: int = 15) -> List[StockImage]:
        if not self.api_key:
            raise AuthenticationError("Pexels requires an API key.")

        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=80)
        cached = self._get_cached_results(clean_term, safe_limit)
        if cached is not None:
            return cached

        url = f"{self.base_url}/search"
        headers = {"Authorization": self.api_key}
        params = {"query": clean_term, "per_page": safe_limit}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(clean_term, safe_limit, images, response.headers)
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(f"Failed to fetch from Pexels: {self._mask_error(e)}")
