import re
from typing import List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from ..base import BaseFetcher
from ..cache import BaseCache
from ..exceptions import APIConnectionError
from ..models import StockImage


def _normalize_flickr_url(raw_url: str) -> str:
    """Ensure Flickr image URLs have a valid https scheme."""
    if not raw_url:
        return ""
    if raw_url.startswith("//"):
        return f"https:{raw_url}"
    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url
    return f"https://{raw_url.lstrip('/')}"


class FlickrClient(BaseFetcher):
    """Client for scraping copyright-free images from Flickr."""

    def __init__(self, api_key: str = "", cache: Optional[BaseCache] = None):
        super().__init__(api_key=api_key, cache=cache)
        self.base_url = "https://www.flickr.com/search/"
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; StockFetcher/0.3.0)"}

    @property
    def name(self) -> str:
        return "flickr"

    def _parse_html(self, html_text: str, limit: int) -> List[StockImage]:
        soup = BeautifulSoup(html_text, "html.parser")
        images: List[StockImage] = []

        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue

            normalized_src = _normalize_flickr_url(src)
            parsed_src = urlparse(normalized_src)
            hostname = (parsed_src.hostname or "").lower()
            if hostname == "staticflickr.com" or hostname.endswith(".staticflickr.com"):
                hi_res = re.sub(r"_[a-z]\.jpg", "_b.jpg", normalized_src)
                img_id = hi_res.split("/")[-1].split("_")[0]

                if any(existing.id == img_id for existing in images):
                    continue

                images.append(
                    StockImage(
                        id=img_id,
                        source="flickr",
                        url_page=f"https://www.flickr.com/photo.gne?id={img_id}",
                        url_original=hi_res,
                        url_thumb=normalized_src,
                        title=img.get("alt") or "",
                    )
                )

                if len(images) >= limit:
                    break

        return images

    def search(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> List[StockImage]:
        clean_term, _ = self.sanitize_search_params(term, limit, max_limit=50)
        safe_limit, norm_page, _ = self.normalize_pagination(
            limit=limit, page=page, cursor=cursor, max_limit=50
        )

        cached = self._get_cached_results(clean_term, safe_limit, page=norm_page)
        if cached is not None:
            return cached

        params = {
            "text": clean_term,
            "license": "4,5,6,9,10",
            "page": norm_page,
        }
        try:
            with httpx.Client(headers=self.headers, timeout=30.0) as client:
                response = self._request_with_retry(
                    client, "GET", self.base_url, params=params
                )
                response.raise_for_status()
                images = self._parse_html(response.text, safe_limit)
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers, page=norm_page
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(f"Failed to fetch from Flickr: {e}")

    async def asearch(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> List[StockImage]:
        clean_term, _ = self.sanitize_search_params(term, limit, max_limit=50)
        safe_limit, norm_page, _ = self.normalize_pagination(
            limit=limit, page=page, cursor=cursor, max_limit=50
        )

        cached = self._get_cached_results(clean_term, safe_limit, page=norm_page)
        if cached is not None:
            return cached

        params = {
            "text": clean_term,
            "license": "4,5,6,9,10",
            "page": norm_page,
        }
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await self._arequest_with_retry(
                    client, "GET", self.base_url, params=params
                )
                response.raise_for_status()
                images = self._parse_html(response.text, safe_limit)
                self._save_cached_results(
                    clean_term, safe_limit, images, response.headers, page=norm_page
                )
                return images
        except httpx.HTTPError as e:
            raise APIConnectionError(f"Failed to fetch from Flickr: {e}")
