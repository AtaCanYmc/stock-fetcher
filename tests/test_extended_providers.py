import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure src takes precedence over installed packages
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

# Mock dependencies if running in a bare runner
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

from stock_fetcher import ClientFactory, MemoryCache, StockImage
from stock_fetcher.clients.openverse import OpenverseClient
from stock_fetcher.clients.wikimedia import WikimediaClient


class ExtendedProvidersTest(unittest.TestCase):
    """Test suite for Wikimedia Commons and Openverse client integrations."""

    def setUp(self):
        self.wiki_client = WikimediaClient()
        self.openverse_client = OpenverseClient(api_key="ov_secret_key_123")

    def test_provider_registration(self):
        """Verify new providers are properly registered in ClientFactory."""
        self.assertIn("wikimedia", ClientFactory._clients)
        self.assertIn("openverse", ClientFactory._clients)

        wiki = ClientFactory.get("wikimedia")
        self.assertIsInstance(wiki, WikimediaClient)
        self.assertEqual(wiki.name, "wikimedia")

        ov = ClientFactory.get("openverse")
        self.assertIsInstance(ov, OpenverseClient)
        self.assertEqual(ov.name, "openverse")

    def test_wikimedia_payload_parsing(self):
        """Verify Wikimedia MediaWiki response payload parses into StockImage models."""
        sample_payload = {
            "query": {
                "pages": [
                    {
                        "pageid": 1049281,
                        "title": "File:Matterhorn Sunrise Panorama.jpg",
                        "imageinfo": [
                            {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Matterhorn.jpg",
                                "descriptionurl": "https://commons.wikimedia.org/wiki/File:Matterhorn.jpg",
                                "thumburl": "https://thumb.wikimedia.org/thumb/Matterhorn.jpg/400px.jpg",
                                "width": 4000,
                                "height": 2500,
                                "size": 3450123,
                                "mime": "image/jpeg",
                                "extmetadata": {
                                    "Artist": {
                                        "value": '<a href="https://example.com">Hans Muster</a>'
                                    },
                                    "LicenseShortName": {"value": "CC BY-SA 4.0"},
                                },
                            }
                        ],
                    }
                ]
            }
        }

        images = self.wiki_client._parse_payload(sample_payload)
        self.assertEqual(len(images), 1)
        img = images[0]
        self.assertEqual(img.source, "wikimedia")
        self.assertEqual(img.id, "1049281")
        self.assertEqual(img.title, "Matterhorn Sunrise Panorama.jpg")
        self.assertEqual(img.author, "Hans Muster")
        self.assertEqual(img.width, 4000)
        self.assertEqual(img.height, 2500)
        self.assertEqual(img.extra.get("license"), "CC BY-SA 4.0")
        self.assertEqual(
            img.url_original,
            "https://upload.wikimedia.org/wikipedia/commons/a/a1/Matterhorn.jpg",
        )
        self.assertEqual(
            img.url_thumb,
            "https://thumb.wikimedia.org/thumb/Matterhorn.jpg/400px.jpg",
        )

    def test_openverse_payload_parsing(self):
        """Verify Openverse JSON payload parses into StockImage models."""
        sample_payload = {
            "results": [
                {
                    "id": "abc-123-def",
                    "title": "Dolomite Alpine Ridge",
                    "foreign_landing_url": "https://openverse.org/image/abc-123-def",
                    "url": "https://images.example.com/original.jpg",
                    "thumbnail": "https://images.example.com/thumb.jpg",
                    "creator": "Elena Rostova",
                    "width": 1920,
                    "height": 1080,
                    "license": "cc0",
                    "license_version": "1.0",
                    "provider": "flickr",
                    "attribution": "Dolomite by Elena Rostova (CC0)",
                }
            ]
        }

        images = self.openverse_client._parse_payload(sample_payload)
        self.assertEqual(len(images), 1)
        img = images[0]
        self.assertEqual(img.source, "openverse")
        self.assertEqual(img.id, "abc-123-def")
        self.assertEqual(img.title, "Dolomite Alpine Ridge")
        self.assertEqual(img.author, "Elena Rostova")
        self.assertEqual(img.width, 1920)
        self.assertEqual(img.height, 1080)
        self.assertEqual(img.extra.get("license"), "cc0")
        self.assertEqual(img.url_original, "https://images.example.com/original.jpg")
        self.assertEqual(img.url_thumb, "https://images.example.com/thumb.jpg")

    def test_openverse_headers_with_and_without_key(self):
        """Verify Openverse authorization headers are applied conditionally."""
        client_with_key = OpenverseClient(api_key="secret_token")
        headers = client_with_key._get_headers()
        self.assertEqual(headers["Authorization"], "Bearer secret_token")

        client_without_key = OpenverseClient()
        headers_no_key = client_without_key._get_headers()
        self.assertNotIn("Authorization", headers_no_key)

    def test_openverse_error_masking(self):
        """Ensure API tokens are masked in Openverse error messages."""
        exc = Exception("HTTP 401 Unauthorized for token ov_secret_key_123 on api")
        masked = self.openverse_client._mask_error(exc)
        self.assertNotIn("ov_secret_key_123", masked)
        self.assertIn("***", masked)

    def test_caching_layer_integration(self):
        """Verify both clients honor the caching layer."""
        cache = MemoryCache()
        client = WikimediaClient(cache=cache)

        # Populate cache directly
        mock_image = StockImage(
            id="cached-99",
            source="wikimedia",
            url_page="https://commons.wikimedia.org/wiki/File:Test.jpg",
            url_original="https://upload.wikimedia.org/test.jpg",
            title="Cached Test",
        )
        client._save_cached_results("mountain", 5, [mock_image], headers={})

        cached_images = client.search("mountain", limit=5)
        self.assertEqual(len(cached_images), 1)
        self.assertEqual(cached_images[0].id, "cached-99")

    @patch("httpx.Client.get")
    def test_wikimedia_sync_search(self, mock_get):
        """Test synchronous search for WikimediaClient."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Cache-Control": "max-age=1800"}
        mock_resp.json.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 55,
                        "title": "File:Test.jpg",
                        "imageinfo": [
                            {
                                "url": "https://upload.wikimedia.org/test.jpg",
                                "thumburl": "https://thumb.wikimedia.org/test.jpg",
                            }
                        ],
                    }
                ]
            }
        }
        mock_get.return_value = mock_resp

        results = self.wiki_client.search("alps", limit=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "55")

    def test_async_search_extended_providers(self):
        """Test asynchronous asearch for both Wikimedia and Openverse."""

        async def run_test():
            mock_wiki_resp = MagicMock()
            mock_wiki_resp.status_code = 200
            mock_wiki_resp.headers = {}
            mock_wiki_resp.json.return_value = {
                "query": {
                    "pages": [
                        {
                            "pageid": 101,
                            "title": "File:AsyncWiki.jpg",
                            "imageinfo": [{"url": "https://wiki.org/async.jpg"}],
                        }
                    ]
                }
            }

            mock_ov_resp = MagicMock()
            mock_ov_resp.status_code = 200
            mock_ov_resp.headers = {}
            mock_ov_resp.json.return_value = {
                "results": [
                    {
                        "id": "async-ov-202",
                        "title": "Async Openverse",
                        "url": "https://openverse.org/async.jpg",
                    }
                ]
            }

            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = mock_wiki_resp
                wiki_res = await self.wiki_client.asearch("nordic", limit=2)
                self.assertEqual(len(wiki_res), 1)
                self.assertEqual(wiki_res[0].id, "101")

                mock_get.return_value = mock_ov_resp
                ov_res = await self.openverse_client.asearch("nordic", limit=2)
                self.assertEqual(len(ov_res), 1)
                self.assertEqual(ov_res[0].id, "async-ov-202")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
