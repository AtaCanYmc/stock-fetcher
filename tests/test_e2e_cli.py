import csv
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

# Ensure local src directory takes precedence
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from stock_fetcher.cli.main import app
from stock_fetcher.mcp.server import search_images
from stock_fetcher.models import StockImage


class EndToEndCLITest(unittest.TestCase):
    """End-to-end tests for the stock-fetcher CLI commands and MCP interface."""

    def setUp(self):
        self.runner = CliRunner()

    def test_e2e_cli_version(self):
        result = self.runner.invoke(app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("stock-fetcher version", result.stdout)
        self.assertIn("Python:", result.stdout)
        self.assertIn("Available Providers", result.stdout)

    def test_e2e_cli_providers(self):
        result = self.runner.invoke(app, ["providers"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Supported Providers", result.stdout)
        self.assertIn("wikimedia", result.stdout.lower())
        self.assertIn("openverse", result.stdout.lower())
        self.assertIn("pexels", result.stdout.lower())
        self.assertIn("pixabay", result.stdout.lower())
        self.assertIn("unsplash", result.stdout.lower())
        self.assertIn("flickr", result.stdout.lower())

    def test_e2e_cli_keys(self):
        result = self.runner.invoke(app, ["keys"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Environment API Key Status", result.stdout)
        self.assertIn("PIXABAY_API_KEY", result.stdout)
        self.assertIn("PEXELS_API_KEY", result.stdout)
        self.assertIn("UNSPLASH_API_KEY", result.stdout)

    def test_e2e_cli_search_json_format(self):
        sample_img = StockImage(
            id="101",
            source="wikimedia",
            url_page="https://commons.wikimedia.org/wiki/File:Test.jpg",
            url_original="https://upload.wikimedia.org/test.jpg",
            title="Test Alps Peak",
            author="Photographer One",
        )

        with patch(
            "stock_fetcher.clients.wikimedia.WikimediaClient.search",
            return_value=[sample_img],
        ):
            result = self.runner.invoke(
                app,
                ["search", "wikimedia", "alps", "--limit", "1", "-f", "json"],
            )
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.stdout)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["id"], "101")
            self.assertEqual(data[0]["source"], "wikimedia")
            self.assertEqual(
                data[0]["url_original"], "https://upload.wikimedia.org/test.jpg"
            )

    def test_e2e_cli_search_csv_format(self):
        sample_img = StockImage(
            id="202",
            source="openverse",
            url_page="https://openverse.org/image/202",
            url_original="https://openverse.org/202.jpg",
            title="Nordic Fjord",
        )

        with patch(
            "stock_fetcher.clients.openverse.OpenverseClient.search",
            return_value=[sample_img],
        ):
            result = self.runner.invoke(
                app,
                ["search", "openverse", "fjord", "--limit", "1", "-f", "csv"],
            )
            self.assertEqual(result.exit_code, 0)
            lines = [
                line.strip()
                for line in result.stdout.strip().splitlines()
                if line.strip()
            ]
            reader = list(csv.reader(lines))
            self.assertGreaterEqual(len(reader), 2)
            self.assertEqual(
                reader[0], ["id", "source", "url_page", "url_original", "title"]
            )
            self.assertEqual(reader[1][0], "202")
            self.assertEqual(reader[1][1], "openverse")

    def test_e2e_cli_search_urls_format(self):
        sample_img = StockImage(
            id="303",
            source="flickr",
            url_page="https://flickr.com/303",
            url_original="https://live.staticflickr.com/303_b.jpg",
            title="Glacial Basin",
        )

        with patch(
            "stock_fetcher.clients.flickr.FlickrClient.search",
            return_value=[sample_img],
        ):
            result = self.runner.invoke(
                app,
                ["search", "flickr", "lake", "--limit", "1", "-f", "urls"],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("https://live.staticflickr.com/303_b.jpg", result.stdout)

    def test_e2e_cli_search_pagination_forwarding(self):
        mock_search = MagicMock(return_value=[])
        with patch(
            "stock_fetcher.clients.wikimedia.WikimediaClient.search", mock_search
        ):
            self.runner.invoke(
                app,
                ["search", "wikimedia", "mountain", "--limit", "10", "--page", "3"],
            )
            self.assertTrue(mock_search.called)
            args, kwargs = mock_search.call_args
            self.assertEqual(kwargs.get("page"), 3)
            self.assertEqual(kwargs.get("limit"), 10)

    def test_e2e_cli_find_command(self):
        sample_img = StockImage(
            id="404",
            source="wikimedia",
            url_page="https://commons.wikimedia.org/wiki/File:Matterhorn.jpg",
            url_original="https://upload.wikimedia.org/matterhorn.jpg",
            title="Matterhorn Sunrise",
        )

        with patch(
            "stock_fetcher.factory.ClientFactory.asearch_all",
            return_value={"wikimedia": [sample_img]},
        ):
            result = self.runner.invoke(
                app, ["find", "matterhorn", "--limit", "1", "-f", "json"]
            )
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.stdout)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["id"], "404")

    def test_e2e_cli_download_command_and_traversal_defense(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. Successful download mock
            mock_resp = MagicMock()
            mock_resp.headers = {"content-length": "100"}
            mock_resp.iter_content = lambda chunk_size: [b"fake_image_bytes"]
            mock_resp.raise_for_status = MagicMock()

            with patch("requests.get", return_value=mock_resp):
                result = self.runner.invoke(
                    app,
                    [
                        "download",
                        "https://images.example.com/photo.jpg",
                        "-o",
                        tmp_dir,
                        "-n",
                        "safe_photo.jpg",
                    ],
                )
                self.assertEqual(result.exit_code, 0)
                downloaded_file = os.path.join(tmp_dir, "safe_photo.jpg")
                self.assertTrue(os.path.exists(downloaded_file))

            # 2. Disallowed protocol attack attempt (e.g. file:///etc/passwd)
            result_scheme = self.runner.invoke(
                app,
                [
                    "download",
                    "file:///etc/passwd",
                    "-o",
                    tmp_dir,
                    "-n",
                    "passwd.jpg",
                ],
            )
            self.assertNotEqual(result_scheme.exit_code, 0)
            self.assertIn("Disallowed protocol scheme", result_scheme.stdout)

    def test_e2e_mcp_tool_execution(self):
        sample_img = StockImage(
            id="mcp-99",
            source="wikimedia",
            url_page="https://commons.wikimedia.org/wiki/File:Mcp.jpg",
            url_original="https://upload.wikimedia.org/mcp.jpg",
            title="MCP Tool Peak",
        )

        with patch(
            "stock_fetcher.clients.wikimedia.WikimediaClient.search",
            return_value=[sample_img],
        ):
            res_str = search_images(
                provider="wikimedia", term="summit", limit=1, page=1
            )
            self.assertIn("Found 1 images", res_str)
            self.assertIn("mcp-99", res_str)
            self.assertIn("https://upload.wikimedia.org/mcp.jpg", res_str)


if __name__ == "__main__":
    unittest.main()
