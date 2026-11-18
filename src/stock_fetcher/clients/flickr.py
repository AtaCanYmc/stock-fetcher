import re
import requests
from bs4 import BeautifulSoup
from typing import List, Any
from ..base import BaseFetcher
from ..exceptions import APIConnectionError


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

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.base_url = "https://www.flickr.com/search/"
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; StockFetcher/0.2.0)"}

    def search(self, term: str, limit: int = 15) -> List[Any]:
        clean_term, safe_limit = self.sanitize_search_params(term, limit, max_limit=50)
        params = {"text": clean_term, "license": "4,5,6,9,10"}

        try:
            response = requests.get(
                self.base_url, params=params, headers=self.headers, timeout=30
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            images = []

            for img in soup.find_all("img"):
                src = img.get("src")
                if not src:
                    continue

                if "staticflickr.com" in src:
                    hi_res = re.sub(r"_[a-z]\.jpg", "_b.jpg", src)
                    img_id = hi_res.split("/")[-1].split("_")[0]

                    # Prevent duplicates
                    if any(existing_img["id"] == img_id for existing_img in images):
                        continue

                    images.append(
                        {
                            "id": img_id,
                            "source": "flickr",
                            "url": _normalize_flickr_url(src),
                            "url_original": _normalize_flickr_url(hi_res),
                        }
                    )

                    if len(images) >= safe_limit:
                        break

            return images
        except requests.RequestException as e:
            raise APIConnectionError(f"Failed to fetch from Flickr: {e}")
