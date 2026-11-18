from typing import Any, Dict, List, Optional

import httpx

from ..base import BaseFetcher
from ..cache import BaseCache
from ..exceptions import APIConnectionError, AuthenticationError
from ..models import StockImage


class PixabayClient(BaseFetcher):
    """Client for fetching copyright-free images from Pixabay."""

    def __init__(self, api_key: str = "", cache: Optional[BaseCache] = None):
        super().__init__(api_key=api_key, cache=cache)
        self.base_url = "https://pixabay.com/api/"

    @property
    def name(self) -> str:
        return "pixabay"

    def _parse_payload(self, data: Dict[str, Any]) -> List[StockImage]:
        if "error" in data:
            raise APIConnectionError(f"Pixabay API error: {data['error']}")

        results: List[StockImage] = []
        for item in data.get("hits", []):
            results.append(
                StockImage(
                    id=str(item.get("id", "")),
                    source="pixabay",
                    url_page=item.get("pageURL", ""),
                    url_original=item.get("largeImageURL", ""),
                    url_thumb=item.get("previewURL", ""),
                    title=item.get("tags", ""),
                    author=item.get("user", ""),
                    width=item.get("imageWidth"),
                    height=item.get("imageHeight"),
                    extra={
                        "views": item.get("views"),
                        "downloads": item.get("downloads"),
                        "likes": item.get("likes"),
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
            raise AuthenticationError("Pixabay requires an API key.")

        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=100)
        cached = self._get_cached_results(clean_term, safe_limit)
        if cached is not None:
            return cached

        params = {
            "key": self.api_key,
            "q": clean_term,
            "per_page": safe_limit,
            "image_type": "photo",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params=params)
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(
                f"Failed to fetch from Pixabay: {self._mask_error(e)}"
            )

    async def asearch(self, term: str, limit: int = 15) -> List[StockImage]:
        if not self.api_key:
            raise AuthenticationError("Pixabay requires an API key.")

        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=100)
        cached = self._get_cached_results(clean_term, safe_limit)
        if cached is not None:
            return cached

        params = {
            "key": self.api_key,
            "q": clean_term,
            "per_page": safe_limit,
            "image_type": "photo",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(
                f"Failed to fetch from Pixabay: {self._mask_error(e)}"
            )
