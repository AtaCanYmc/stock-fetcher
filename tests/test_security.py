import sys
from unittest.mock import MagicMock, patch

# Ensure optional or uninstalled dependencies are mock-shimmed in bare environments
for mod in ("requests", "typer", "rich", "rich.console", "rich.table", "rich.panel", "rich.progress", "bs4"):
    if mod not in sys.modules:
        try:
            __import__(mod)
        except ModuleNotFoundError:
            sys.modules[mod] = MagicMock()

import unittest
import os
import tempfile
from stock_fetcher.base import BaseFetcher
from stock_fetcher.cli.main import _download_single_image


class SecuritySanitizationTest(unittest.TestCase):
    def test_empty_search_term_rejected(self):
        with self.assertRaises(ValueError):
            BaseFetcher.sanitize_search_params("", 10)
        with self.assertRaises(ValueError):
            BaseFetcher.sanitize_search_params("   ", 10)

    def test_limit_clamping(self):
        _, limit = BaseFetcher.sanitize_search_params("cats", -5, max_limit=50)
        self.assertEqual(limit, 1)

        _, limit = BaseFetcher.sanitize_search_params("cats", 9999, max_limit=50)
        self.assertEqual(limit, 50)

    def test_unsupported_protocol_scheme(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(ValueError) as ctx:
                _download_single_image("file:///etc/passwd", tmp_dir)
            self.assertIn("Disallowed protocol scheme", str(ctx.exception))

            with self.assertRaises(ValueError) as ctx:
                _download_single_image("ftp://example.com/image.jpg", tmp_dir)
            self.assertIn("Disallowed protocol scheme", str(ctx.exception))

    @patch("requests.get")
    def test_path_traversal_prevention(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "16"}
        mock_response.iter_content.return_value = [b"mock image bytes"]
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = _download_single_image(
                url="https://example.com/valid.jpg",
                output_dir=tmp_dir,
                filename="../../escaped.jpg",
            )
            canonical_tmp = os.path.realpath(tmp_dir)
            canonical_target = os.path.realpath(target)
            self.assertTrue(canonical_target.startswith(canonical_tmp))
            self.assertEqual(os.path.basename(target), "escaped.jpg")
            self.assertTrue(os.path.exists(target))


if __name__ == "__main__":
    unittest.main()
