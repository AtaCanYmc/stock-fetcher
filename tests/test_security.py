import os
import stat
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure optional or uninstalled dependencies are mock-shimmed in bare environments
for mod in (
    "requests",
    "typer",
    "rich",
    "rich.console",
    "rich.table",
    "rich.panel",
    "rich.progress",
    "bs4",
):
    if mod not in sys.modules:
        try:
            __import__(mod)
        except ModuleNotFoundError:
            sys.modules[mod] = MagicMock()

# Ensure local src directory takes precedence
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from stock_fetcher.base import BaseFetcher
from stock_fetcher.cache import DiskCache
from stock_fetcher.cli.main import (
    _download_single_image,
    _validate_safe_public_host,
)
from stock_fetcher.pagination import decode_cursor


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

    def test_null_byte_and_length_capping(self):
        # Null bytes should be stripped
        term, _ = BaseFetcher.sanitize_search_params("mountains\0injection", 10)
        self.assertEqual(term, "mountainsinjection")

        # Extremely long query string capped to 500 characters
        long_term = "a" * 1000
        clean_term, _ = BaseFetcher.sanitize_search_params(long_term, 10)
        self.assertEqual(len(clean_term), 500)

    def test_unsupported_protocol_scheme(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(ValueError) as ctx:
                _download_single_image("file:///etc/passwd", tmp_dir)
            self.assertIn("Disallowed protocol scheme", str(ctx.exception))

            with self.assertRaises(ValueError) as ctx:
                _download_single_image("ftp://example.com/image.jpg", tmp_dir)
            self.assertIn("Disallowed protocol scheme", str(ctx.exception))

    def test_ssrf_private_and_loopback_ips_blocked(self):
        # Loopback and private IP literals must be rejected
        for host in (
            "127.0.0.1",
            "localhost",
            "10.0.0.1",
            "192.168.1.10",
            "169.254.169.254",
            "::1",
        ):
            with self.assertRaises(ValueError) as ctx:
                _validate_safe_public_host(host)
            self.assertIn("Disallowed destination", str(ctx.exception))

    @patch("stock_fetcher.cli.main._validate_safe_public_host")
    @patch("requests.get")
    def test_path_traversal_prevention(self, mock_get, mock_val):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "16"}
        mock_response.iter_content.return_value = [b"mock image bytes"]
        mock_response.is_redirect = False
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = _download_single_image(
                url="https://images.example.com/valid.jpg",
                output_dir=tmp_dir,
                filename="../../escaped.jpg",
            )
            canonical_tmp = os.path.realpath(tmp_dir)
            canonical_target = os.path.realpath(target)
            self.assertTrue(canonical_target.startswith(canonical_tmp))
            self.assertEqual(os.path.basename(target), "escaped.jpg")
            self.assertTrue(os.path.exists(target))

    @patch("stock_fetcher.cli.main._validate_safe_public_host")
    @patch("requests.get")
    def test_disallowed_extension_neutralized(self, mock_get, mock_val):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "16"}
        mock_response.iter_content.return_value = [b"mock image bytes"]
        mock_response.is_redirect = False
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = _download_single_image(
                url="https://images.example.com/photo.png",
                output_dir=tmp_dir,
                filename="payload.sh",
            )
            self.assertTrue(target.endswith(".sh.jpg"))
            self.assertTrue(os.path.exists(target))

    @patch("stock_fetcher.cli.main._validate_safe_public_host")
    @patch("requests.get")
    def test_safe_file_permissions(self, mock_get, mock_val):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "16"}
        mock_response.iter_content.return_value = [b"mock image bytes"]
        mock_response.is_redirect = False
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = _download_single_image(
                url="https://images.example.com/photo.jpg",
                output_dir=tmp_dir,
                filename="photo.jpg",
            )
            mode = stat.S_IMODE(os.stat(target).st_mode)
            self.assertEqual(mode, 0o600)

    def test_disk_cache_dir_permissions(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_path = os.path.join(tmp_dir, "test_cache")
            _ = DiskCache(cache_dir=cache_path)
            mode = stat.S_IMODE(os.stat(cache_path).st_mode)
            self.assertEqual(mode, 0o700)

    def test_enhanced_credential_masking(self):
        class DummyFetcher(BaseFetcher):
            @property
            def name(self):
                return "dummy"

            def search(self, *a, **k):
                return []

            async def asearch(self, *a, **k):
                return []

        fetcher = DummyFetcher(api_key="secret+key/123==")
        # Raw key in exception
        msg1 = fetcher._mask_error(Exception("Connection failed for secret+key/123=="))
        self.assertNotIn("secret+key/123==", msg1)
        self.assertIn("***", msg1)

        # Percent-encoded key in exception URL
        msg2 = fetcher._mask_error(
            Exception("Failed GET https://api.com?key=secret%2Bkey%2F123%3D%3D")
        )
        self.assertNotIn("secret%2Bkey%2F123%3D%3D", msg2)
        self.assertIn("***", msg2)

        # Bearer token in header representation
        msg3 = fetcher._mask_error(
            Exception("Headers: Authorization: Bearer abc12345xyz")
        )
        self.assertNotIn("abc12345xyz", msg3)
        self.assertIn("Bearer ***", msg3)

    def test_cursor_decompression_bomb_prevention(self):
        huge_cursor = "A" * 5000
        page, offset = decode_cursor(huge_cursor)
        self.assertEqual((page, offset), (1, 0))


if __name__ == "__main__":
    unittest.main()
