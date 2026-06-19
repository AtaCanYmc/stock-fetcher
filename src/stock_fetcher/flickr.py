import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseFetcher
from .exceptions import FetcherError

class FlickrClient(BaseFetcher):
    def __init__(self, api_key: str = ""):
        # Flickr scrapper doesn't need an API key in this implementation
        super().__init__(api_key)
        self.base_url = "https://www.flickr.com/search/"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def search_images(self, query: str, per_page: int = 15, page: int = 1) -> List[Dict[str, Any]]:
        # Note: the scrapper currently does not support pagination directly in the same way 
        # as the APIs do, but we keep the signature for consistency.
        params = {
            "text": query,
            "license": "4,5,6,9,10"
        }

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=30)
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

                    images.append({
                        "id": img_id,
                        "source": "flickr",
                        "url": f"https:{src}", # Thumbnail URL as page URL fallback
                        "url_original": f"https:{hi_res}",
                        "url_thumbnail": f"https:{src}",
                    })
                    
                    if len(images) >= per_page:
                        break
                        
            return images
        except requests.RequestException as e:
            raise FetcherError(f"Failed to fetch images from Flickr: {e}")

    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        # Since this is a scrapper and we don't have a direct endpoint for single image details easily,
        # we raise a NotImplementedError or mock it.
        raise FetcherError("get_image_details is not supported for Flickr scrapper client.")
