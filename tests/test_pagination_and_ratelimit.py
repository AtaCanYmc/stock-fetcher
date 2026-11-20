import asyncio
import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

import httpx

# Ensure local src directory takes precedence
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from stock_fetcher.cache import build_cache_key
from stock_fetcher.clients.pexels import PexelsClient
from stock_fetcher.clients.wikimedia import WikimediaClient
from stock_fetcher.exceptions import RateLimitExceededError
from stock_fetcher.models import StockImage
from stock_fetcher.pagination import (
    build_next_cursor,
    build_prev_cursor,
    decode_cursor,
    encode_cursor,
    normalize_pagination,
)
from stock_fetcher.rate_limit import (
    AdaptiveRateLimiter,
    parse_rate_limit_headers,
)


class PaginationTest(unittest.TestCase):
    """Test deterministic pagination cursor normalization and encoding."""

    def test_cursor_roundtrip_encoding(self):
        cursor = encode_cursor(page=3, offset=30)
        self.assertIsInstance(cursor, str)
        page, offset = decode_cursor(cursor)
        self.assertEqual(page, 3)
        self.assertEqual(offset, 30)

    def test_decode_fallback_formats(self):
        # Plain digit string
        self.assertEqual(decode_cursor("5"), (5, 0))
        # "p" prefix
        self.assertEqual(decode_cursor("p4"), (4, 0))
        # None or invalid base64
        self.assertEqual(decode_cursor(None), (1, 0))
        self.assertEqual(decode_cursor(""), (1, 0))
        self.assertEqual(decode_cursor("%%%invalid-b64%%%"), (1, 0))

    def test_normalize_pagination_variations(self):
        # 1. Default first page
        limit, page, offset = normalize_pagination(limit=10)
        self.assertEqual((limit, page, offset), (10, 1, 0))

        # 2. Page specified
        limit, page, offset = normalize_pagination(limit=15, page=4)
        self.assertEqual((limit, page, offset), (15, 4, 45))

        # 3. Direct offset specified
        limit, page, offset = normalize_pagination(limit=20, offset=60)
        self.assertEqual((limit, page, offset), (20, 4, 60))

        # 4. Cursor specified
        c = encode_cursor(page=5, offset=100)
        limit, page, offset = normalize_pagination(limit=25, cursor=c)
        self.assertEqual((limit, page, offset), (25, 5, 100))

    def test_build_next_and_prev_cursors(self):
        # If returned fewer than limit -> has_more is False -> next_cursor is None
        self.assertIsNone(
            build_next_cursor(page=1, limit=10, returned_count=8, offset=0)
        )

        # Full page returned -> next cursor computed
        next_c = build_next_cursor(page=1, limit=10, returned_count=10, offset=0)
        self.assertIsNotNone(next_c)
        p, off = decode_cursor(next_c)
        self.assertEqual(p, 2)
        self.assertEqual(off, 10)

        # Prev cursor on page 1 is None
        self.assertIsNone(build_prev_cursor(page=1, limit=10, offset=0))

        # Prev cursor on page 3 points to page 2
        prev_c = build_prev_cursor(page=3, limit=10, offset=20)
        self.assertIsNotNone(prev_c)
        p, off = decode_cursor(prev_c)
        self.assertEqual(p, 2)
        self.assertEqual(off, 10)

    def test_cache_key_isolation_by_page(self):
        key_p1 = build_cache_key("pexels", "aurora", 10, page=1)
        key_p2 = build_cache_key("pexels", "aurora", 10, page=2)
        self.assertEqual(key_p1, "pexels:aurora:10")
        self.assertEqual(key_p2, "pexels:aurora:10:p2")
        self.assertNotEqual(key_p1, key_p2)

    def test_paginated_result_wrapper(self):
        client = PexelsClient(api_key="test_key")
        sample_img = StockImage(
            id="1",
            source="pexels",
            url_page="https://pexels.com/1",
            url_original="https://images.pexels.com/1.jpg",
        )

        with patch.object(client, "search", return_value=[sample_img] * 10):
            res = client.search_paginated("forest", limit=10, page=2)
            self.assertEqual(len(res.items), 10)
            self.assertEqual(res.pagination.page, 2)
            self.assertEqual(res.pagination.offset, 10)
            self.assertTrue(res.pagination.has_more)
            self.assertIsNotNone(res.pagination.next_cursor)
            self.assertIsNotNone(res.pagination.prev_cursor)

    def test_wikimedia_offset_mapping(self):
        client = WikimediaClient()
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.headers = {}
        mock_resp.json.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 101,
                        "title": "File:Glacier.jpg",
                        "imageinfo": [
                            {"url": "http://img", "thumburl": "http://thumb"}
                        ],
                    }
                ]
            }
        }

        with patch("httpx.Client.request", return_value=mock_resp) as mock_req:
            client.search("glacier", limit=15, page=3)
            # offset for page 3 with limit 15 should be (3 - 1) * 15 = 30
            self.assertTrue(mock_req.called)
            called_params = mock_req.call_args[1].get("params", {})
            self.assertEqual(called_params.get("gsroffset"), 30)
            self.assertEqual(called_params.get("gsrlimit"), 15)


class RateLimiterTest(unittest.TestCase):
    """Test rate limit header parsing, adaptive pacing, and exponential backoff."""

    def test_parse_rate_limit_headers(self):
        # 1. Pexels / standard format
        headers = {
            "X-Ratelimit-Limit": "200",
            "X-Ratelimit-Remaining": "42",
            "X-Ratelimit-Reset": "15",
        }
        info = parse_rate_limit_headers(headers)
        self.assertEqual(info.limit, 200)
        self.assertEqual(info.remaining, 42)
        self.assertEqual(info.reset_seconds, 15.0)

        # 2. Retry-After format (429 response)
        headers_429 = {
            "Retry-After": "45",
            "X-RateLimit-Remaining": "0",
        }
        info_429 = parse_rate_limit_headers(headers_429)
        self.assertEqual(info_429.reset_seconds, 45.0)
        self.assertEqual(info_429.remaining, 0)

        # 3. Epoch timestamp in reset header (> 1e9)
        future_ts = time.time() + 60.0
        headers_epoch = {"x-ratelimit-reset": str(future_ts)}
        info_epoch = parse_rate_limit_headers(headers_epoch)
        self.assertAlmostEqual(info_epoch.reset_seconds, 60.0, delta=2.0)

    def test_adaptive_pacing_when_quota_low(self):
        limiter = AdaptiveRateLimiter()
        # Initial pacing is 0
        self.assertEqual(limiter.get_pacing_delay("pexels"), 0.0)

        # Record a response with remaining = 1
        resp = MagicMock(spec=httpx.Response)
        resp.headers = {
            "x-ratelimit-remaining": "1",
            "x-ratelimit-reset": "0.8",
        }
        limiter.record_response("pexels", resp)

        # Pacing should now be activated
        pacing = limiter.get_pacing_delay("pexels")
        self.assertGreater(pacing, 0.0)
        self.assertLessEqual(pacing, 1.0)

    def test_exponential_backoff_retry_success(self):
        limiter = AdaptiveRateLimiter(base_delay=0.01, max_delay=0.1, max_retries=3)

        call_count = 0

        def flaky_request():
            nonlocal call_count
            call_count += 1
            resp = MagicMock(spec=httpx.Response)
            if call_count < 3:
                resp.status_code = 429
                resp.headers = {"Retry-After": "0.01"}
                return resp
            resp.status_code = 200
            resp.headers = {"X-Ratelimit-Remaining": "100"}
            return resp

        final_resp = limiter.execute_sync(flaky_request, provider="test_prov")
        self.assertEqual(final_resp.status_code, 200)
        self.assertEqual(call_count, 3)

    def test_rate_limit_exceeded_error_on_exhaustion(self):
        limiter = AdaptiveRateLimiter(base_delay=0.01, max_delay=0.05, max_retries=2)

        def throttled_request():
            resp = MagicMock(spec=httpx.Response)
            resp.status_code = 429
            resp.headers = {"Retry-After": "10"}
            return resp

        with self.assertRaises(RateLimitExceededError) as ctx:
            limiter.execute_sync(throttled_request, provider="pexels")

        self.assertIn("Exhausted 2 retries", str(ctx.exception))
        self.assertEqual(ctx.exception.retry_after, 10.0)
        self.assertEqual(ctx.exception.provider, "pexels")

    def test_async_exponential_backoff_retry(self):
        limiter = AdaptiveRateLimiter(base_delay=0.01, max_delay=0.05, max_retries=2)
        call_count = 0

        async def aflaky_request():
            nonlocal call_count
            call_count += 1
            resp = MagicMock(spec=httpx.Response)
            if call_count == 1:
                resp.status_code = 429
                resp.headers = {"Retry-After": "0.01"}
                return resp
            resp.status_code = 200
            resp.headers = {"X-Ratelimit-Remaining": "50"}
            return resp

        loop = asyncio.new_event_loop()
        try:
            res = loop.run_until_complete(
                limiter.execute_async(aflaky_request, provider="unsplash")
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(call_count, 2)
        finally:
            loop.close()


if __name__ == "__main__":
    unittest.main()
