from typing import Any, Dict, List, Optional

import httpx

from ..base import BaseFetcher
from ..cache import BaseCache
from ..exceptions import APIConnectionError, AuthenticationError
from ..models import StockImage


class UnsplashClient(BaseFetcher):
    """Client for fetching copyright-free images from Unsplash."""

    def __init__(self, api_key: str = "", cache: Optional[BaseCache] = None):
        super().__init__(api_key=api_key, cache=cache)
        self.base_url = "https://api.unsplash.com"

    @property
    def name(self) -> str:
        return "unsplash"

    def _parse_payload(self, data: Dict[str, Any]) -> List[StockImage]:
        results: List[StockImage] = []
        for item in data.get("results", []):
            links_dict = item.get("links", {})
            urls_dict = item.get("urls", {})
            user_dict = item.get("user", {})
            results.append(
                StockImage(
                    id=str(item.get("id", "")),
                    source="unsplash",
                    url_page=links_dict.get("html", ""),
                    url_original=urls_dict.get("raw") or urls_dict.get("full", ""),
                    url_thumb=urls_dict.get("thumb") or urls_dict.get("small"),
                    title=item.get("description") or item.get("alt_description") or "",
                    author=user_dict.get("username") or user_dict.get("name", ""),
                    width=item.get("width"),
                    height=item.get("height"),
                    extra={
                        "likes": item.get("likes"),
                        "created_at": item.get("created_at"),
                    },
                )
            )
        return results

    def _mask_error(self, exc: Exception) -> str:
        err_msg = str(exc)
        if self.api_key and self.api_key in err_msg:
            err_msg = err_msg.replace(self.api_key, "***")
        return err_msg

    def search(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> List[StockImage]:
        if not self.api_key:
            raise AuthenticationError("Unsplash requires an API key (client_id).")

        clean_term, _ = self.sanitize_search_params(term, limit, max_limit=30)
        safe_limit, norm_page, _ = self.normalize_pagination(
            limit=limit, page=page, cursor=cursor, max_limit=30
        )

        cached = self._get_cached_results(clean_term, safe_limit, page=norm_page)
        if cached is not None:
            return cached

        url = f"{self.base_url}/search/photos"
        params = {
            "query": clean_term,
            "per_page": safe_limit,
            "page": norm_page,
            "client_id": self.api_key,
            "order_by": "relevant",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = self._request_with_retry(client, "GET", url, params=params)
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers, page=norm_page
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(
                f"Failed to fetch from Unsplash: {self._mask_error(e)}"
            )

    async def asearch(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> List[StockImage]:
        if not self.api_key:
            raise AuthenticationError("Unsplash requires an API key (client_id).")

        clean_term, _ = self.sanitize_search_params(term, limit, max_limit=30)
        safe_limit, norm_page, _ = self.normalize_pagination(
            limit=limit, page=page, cursor=cursor, max_limit=30
        )

        cached = self._get_cached_results(clean_term, safe_limit, page=norm_page)
        if cached is not None:
            return cached

        url = f"{self.base_url}/search/photos"
        params = {
            "query": clean_term,
            "per_page": safe_limit,
            "page": norm_page,
            "client_id": self.api_key,
            "order_by": "relevant",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await self._arequest_with_retry(
                    client, "GET", url, params=params
                )
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed with status code {response.status_code}."
                    )
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers, page=norm_page
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(
                f"Failed to fetch from Unsplash: {self._mask_error(e)}"
            )
