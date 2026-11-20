import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
from unittest.mock import MagicMock, patch

# Mock dependencies if running in a bare test runner without installed extras
for mod in (
    "httpx",
    "bs4",
    "requests",
    "typer",
    "rich",
    "rich.console",
    "rich.table",
    "rich.panel",
    "rich.progress",
):
    if mod not in sys.modules:
        try:
            __import__(mod)
        except ModuleNotFoundError:
            sys.modules[mod] = MagicMock()

import unittest

from stock_fetcher.cache import MemoryCache
from stock_fetcher.factory import ClientFactory
from stock_fetcher.models import StockImage


class AsyncClientTest(unittest.IsolatedAsyncioTestCase):
    @patch("httpx.AsyncClient.get")
    async def test_async_search_single_client(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"cache-control": "max-age=600"}
        mock_response.json.return_value = {
            "photos": [
                {
                    "id": 101,
                    "url": "https://www.pexels.com/photo/101/",
                    "photographer": "Jane Doe",
                    "width": 1920,
                    "height": 1080,
                    "src": {
                        "original": "https://images.pexels.com/photos/101/orig.jpg"
                    },
                }
            ]
        }
        mock_get.return_value = mock_response

        client = ClientFactory.get("pexels", api_key="test_token")
        results = await client.asearch("nature", limit=1)

        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertIsInstance(item, StockImage)
        self.assertEqual(item.id, "101")
        self.assertEqual(item.author, "Jane Doe")
        self.assertEqual(
            item.url_original, "https://images.pexels.com/photos/101/orig.jpg"
        )

    @patch("httpx.AsyncClient.get")
    async def test_concurrent_multi_provider_search(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {
            "hits": [
                {
                    "id": 999,
                    "pageURL": "https://pixabay.com/photos/999/",
                    "largeImageURL": "https://pixabay.com/get/999.jpg",
                    "user": "alice",
                }
            ]
        }
        mock_get.return_value = mock_response

        cache = MemoryCache()
        results = await ClientFactory.asearch_all(
            term="galaxy",
            limit=1,
            api_keys={"pixabay": "valid_key"},
            cache=cache,
            providers=["pixabay"],
        )

        self.assertIn("pixabay", results)
        self.assertEqual(len(results["pixabay"]), 1)
        self.assertEqual(results["pixabay"][0].id, "999")


if __name__ == "__main__":
    unittest.main()
