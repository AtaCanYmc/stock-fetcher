from typing import Any, Dict, List, Optional

import httpx

from ..base import BaseFetcher
from ..cache import BaseCache
from ..exceptions import APIConnectionError, AuthenticationError
from ..models import StockImage


class OpenverseClient(BaseFetcher):
    """Client for fetching openly licensed media from Openverse."""

    def __init__(self, api_key: str = "", cache: Optional[BaseCache] = None):
        super().__init__(api_key=api_key, cache=cache)
        self.base_url = "https://api.openverse.org/v1/images/"

    @property
    def name(self) -> str:
        return "openverse"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "stock-fetcher/0.3.0 (https://github.com/AtaCanYmc/stock-fetcher)"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _mask_error(self, exc: Exception) -> str:
        err_msg = str(exc)
        if self.api_key and self.api_key in err_msg:
            err_msg = err_msg.replace(self.api_key, "***")
        return err_msg

    def _parse_payload(self, data: Dict[str, Any]) -> List[StockImage]:
        if "detail" in data:
            raise APIConnectionError(f"Openverse API error: {data['detail']}")

        results: List[StockImage] = []
        for item in data.get("results", []):
            results.append(
                StockImage(
                    id=str(item.get("id", "")),
                    source="openverse",
                    url_page=item.get("foreign_landing_url")
                    or item.get("detail_url", ""),
                    url_original=item.get("url", ""),
                    url_thumb=item.get("thumbnail") or item.get("url", ""),
                    title=item.get("title", "") or "",
                    author=item.get("creator") or None,
                    width=item.get("width"),
                    height=item.get("height"),
                    extra={
                        "license": item.get("license"),
                        "license_version": item.get("license_version"),
                        "provider": item.get("provider"),
                        "attribution": item.get("attribution"),
                    },
                )
            )
        return results

    def search(self, term: str, limit: int = 15) -> List[StockImage]:
        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=100)
        cached = self._get_cached_results(clean_term, safe_limit)
        if cached is not None:
            return cached

        params = {
            "q": clean_term,
            "page_size": safe_limit,
        }

        try:
            with httpx.Client(timeout=30.0, headers=self._get_headers()) as client:
                response = client.get(self.base_url, params=params)
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Openverse authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(
                f"Failed to fetch from Openverse: {self._mask_error(e)}"
            )

    async def asearch(self, term: str, limit: int = 15) -> List[StockImage]:
        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=100)
        cached = self._get_cached_results(clean_term, safe_limit)
        if cached is not None:
            return cached

        params = {
            "q": clean_term,
            "page_size": safe_limit,
        }

        try:
            async with httpx.AsyncClient(
                timeout=30.0, headers=self._get_headers()
            ) as client:
                response = await client.get(self.base_url, params=params)
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Openverse authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(
                f"Failed to fetch from Openverse: {self._mask_error(e)}"
            )
