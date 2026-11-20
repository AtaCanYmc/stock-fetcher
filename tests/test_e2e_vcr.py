import os
import sys
import unittest
from urllib.parse import urlparse

import vcr

# Ensure local src directory takes precedence
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from stock_fetcher.clients.flickr import FlickrClient
from stock_fetcher.clients.openverse import OpenverseClient
from stock_fetcher.clients.pexels import PexelsClient
from stock_fetcher.clients.pixabay import PixabayClient
from stock_fetcher.clients.unsplash import UnsplashClient
from stock_fetcher.clients.wikimedia import WikimediaClient
from stock_fetcher.models import StockImage

CASSETTES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures/vcr_cassettes")
)

# Offline VCR runner ensuring tests execute deterministically against recorded cassettes
recorder = vcr.VCR(
    serializer="yaml",
    cassette_library_dir=CASSETTES_DIR,
    record_mode="none",
    decode_compressed_response=True,
)


class VCRNetworkFixturesEndToEndTest(unittest.TestCase):
    """End-to-end integration tests using recorded network fixtures via VCR.py."""

    def test_e2e_pexels_cassette(self):
        with recorder.use_cassette("pexels_search.yaml"):
            client = PexelsClient(api_key="test-token")
            results = client.search("ocean", limit=2, page=1)

            self.assertEqual(len(results), 2)
            for img in results:
                self.assertIsInstance(img, StockImage)
                self.assertEqual(img.source, "pexels")
                self.assertEqual(
                    urlparse(img.url_original).hostname, "images.pexels.com"
                )
                self.assertEqual(urlparse(img.url_thumb).hostname, "images.pexels.com")
                self.assertIn(img.id, ("12345", "67890"))

            # Rate limit info parsed from cassette headers
            r_info = client.rate_limit_info
            self.assertIsNotNone(r_info)
            self.assertEqual(r_info.limit, 200)
            self.assertEqual(r_info.remaining, 198)

    def test_e2e_pixabay_cassette(self):
        with recorder.use_cassette("pixabay_search.yaml"):
            client = PixabayClient(api_key="test-key")
            results = client.search("aurora", limit=2, page=1)

            self.assertEqual(len(results), 2)
            for img in results:
                self.assertIsInstance(img, StockImage)
                self.assertEqual(img.source, "pixabay")
                self.assertEqual(urlparse(img.url_original).hostname, "pixabay.com")
                self.assertIn("aurora", img.title.lower())

            r_info = client.rate_limit_info
            self.assertIsNotNone(r_info)
            self.assertEqual(r_info.limit, 100)
            self.assertEqual(r_info.remaining, 95)

    def test_e2e_unsplash_cassette(self):
        with recorder.use_cassette("unsplash_search.yaml"):
            client = UnsplashClient(api_key="test-client-id")
            results = client.search("forest", limit=2, page=1)

            self.assertEqual(len(results), 2)
            for img in results:
                self.assertIsInstance(img, StockImage)
                self.assertEqual(img.source, "unsplash")
                self.assertEqual(
                    urlparse(img.url_original).hostname, "images.unsplash.com"
                )
                self.assertTrue(
                    img.author
                    in ("forestwalker", "canopyview", "Forest Walker", "Canopy View")
                )

            r_info = client.rate_limit_info
            self.assertIsNotNone(r_info)
            self.assertEqual(r_info.limit, 50)
            self.assertEqual(r_info.remaining, 47)

    def test_e2e_flickr_cassette(self):
        with recorder.use_cassette("flickr_search.yaml"):
            client = FlickrClient()
            results = client.search("alps", limit=2, page=1)

            self.assertEqual(len(results), 2)
            for img in results:
                self.assertIsInstance(img, StockImage)
                self.assertEqual(img.source, "flickr")
                self.assertEqual(
                    urlparse(img.url_original).hostname, "live.staticflickr.com"
                )
                self.assertTrue(img.url_original.endswith("_b.jpg"))

    def test_e2e_wikimedia_cassette(self):
        with recorder.use_cassette("wikimedia_search.yaml"):
            client = WikimediaClient()
            results = client.search("mountain", limit=2, page=1)

            self.assertGreaterEqual(len(results), 1)
            for img in results:
                self.assertIsInstance(img, StockImage)
                self.assertEqual(img.source, "wikimedia")
                self.assertEqual(
                    urlparse(img.url_original).hostname, "upload.wikimedia.org"
                )
                self.assertEqual(
                    urlparse(img.url_page).hostname, "commons.wikimedia.org"
                )

    def test_e2e_openverse_cassette(self):
        with recorder.use_cassette("openverse_search.yaml"):
            client = OpenverseClient()
            results = client.search("lake", limit=2, page=1)

            self.assertEqual(len(results), 2)
            for img in results:
                self.assertIsInstance(img, StockImage)
                self.assertEqual(img.source, "openverse")
                self.assertEqual(img.author, "barnyz")
                self.assertIn("CC BY-NC-ND 2.0", img.extra.get("attribution", ""))

    def test_e2e_paginated_result_with_cassette(self):
        with recorder.use_cassette("pexels_search.yaml"):
            client = PexelsClient(api_key="test-token")
            paginated = client.search_paginated("ocean", limit=2, page=1)

            self.assertEqual(len(paginated.items), 2)
            self.assertEqual(paginated.pagination.page, 1)
            self.assertEqual(paginated.pagination.limit, 2)
            self.assertTrue(paginated.pagination.has_more)
            self.assertIsNotNone(paginated.pagination.next_cursor)


if __name__ == "__main__":
    unittest.main()
