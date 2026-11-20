import re
from typing import Any, Dict, List, Optional

import httpx

from ..base import BaseFetcher
from ..cache import BaseCache
from ..exceptions import APIConnectionError
from ..models import StockImage


def _strip_html(text: Optional[str]) -> str:
    """Remove HTML tags from metadata strings."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return " ".join(clean.split())


class WikimediaClient(BaseFetcher):
    """Client for fetching public domain and Creative Commons media from Wikimedia Commons."""

    def __init__(self, api_key: str = "", cache: Optional[BaseCache] = None):
        super().__init__(api_key=api_key, cache=cache)
        self.base_url = "https://commons.wikimedia.org/w/api.php"
        self.headers = {
            "User-Agent": "stock-fetcher/0.3.0 (https://github.com/AtaCanYmc/stock-fetcher)"
        }

    @property
    def name(self) -> str:
        return "wikimedia"

    def _parse_payload(self, data: Dict[str, Any]) -> List[StockImage]:
        if "error" in data:
            err_info = data["error"].get("info", "Unknown Wikimedia error")
            raise APIConnectionError(f"Wikimedia API error: {err_info}")

        results: List[StockImage] = []
        pages = data.get("query", {}).get("pages", [])
        for page in pages:
            # Skip missing pages
            if page.get("missing"):
                continue

            image_infos = page.get("imageinfo", [])
            if not image_infos:
                continue

            info = image_infos[0]
            extmeta = info.get("extmetadata", {})

            # Clean File: prefix from title
            raw_title = page.get("title", "")
            clean_title = re.sub(r"^File:", "", raw_title, flags=re.IGNORECASE).strip()

            author = _strip_html(extmeta.get("Artist", {}).get("value"))
            license_name = extmeta.get("LicenseShortName", {}).get("value", "")

            results.append(
                StockImage(
                    id=str(page.get("pageid") or raw_title),
                    source="wikimedia",
                    url_page=info.get("descriptionurl")
                    or f"https://commons.wikimedia.org/wiki/{raw_title}",
                    url_original=info.get("url", ""),
                    url_thumb=info.get("thumburl") or info.get("url", ""),
                    title=clean_title,
                    author=author or None,
                    width=info.get("width"),
                    height=info.get("height"),
                    extra={
                        "license": license_name,
                        "size_bytes": info.get("size"),
                        "mime": info.get("mime"),
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
            "action": "query",
            "generator": "search",
            "gsrsearch": clean_term,
            "gsrnamespace": "6",
            "gsrlimit": safe_limit,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
            "iiurlwidth": "400",
            "format": "json",
            "formatversion": "2",
        }

        try:
            with httpx.Client(timeout=30.0, headers=self.headers) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(f"Failed to fetch from Wikimedia Commons: {e}")

    async def asearch(self, term: str, limit: int = 15) -> List[StockImage]:
        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=100)
        cached = self._get_cached_results(clean_term, safe_limit)
        if cached is not None:
            return cached

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": clean_term,
            "gsrnamespace": "6",
            "gsrlimit": safe_limit,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
            "iiurlwidth": "400",
            "format": "json",
            "formatversion": "2",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                images = self._parse_payload(response.json())
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(f"Failed to fetch from Wikimedia Commons: {e}")
