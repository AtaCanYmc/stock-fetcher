import unittest
import time
import tempfile
from stock_fetcher.cache import (
    MemoryCache,
    DiskCache,
    build_cache_key,
    parse_cache_control_ttl,
)


class CacheTest(unittest.TestCase):
    def test_cache_key_generation(self):
        key = build_cache_key("Pixabay", "  Forest  ", 5)
        self.assertEqual(key, "pixabay:forest:5")

    def test_parse_cache_control_ttl(self):
        self.assertEqual(parse_cache_control_ttl({"cache-control": "public, max-age=3600"}), 3600)
        self.assertEqual(parse_cache_control_ttl({"Cache-Control": "max-age=120, must-revalidate"}), 120)
        self.assertEqual(parse_cache_control_ttl({"cache-control": "no-store"}), 0)
        self.assertIsNone(parse_cache_control_ttl({}))

    def test_memory_cache_ttl_and_expiry(self):
        cache = MemoryCache(default_ttl=1)
        test_data = [{"id": "1", "source": "test"}]

        cache.set("key1", test_data, ttl=1)
        self.assertEqual(cache.get("key1"), test_data)

        # Wait for expiration
        time.sleep(1.05)
        self.assertIsNone(cache.get("key1"))

    def test_disk_cache_persistence_and_clear(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = DiskCache(cache_dir=tmp_dir, default_ttl=3600)
            test_data = [{"id": "100", "source": "flickr"}]

            cache.set("flickr:cars:2", test_data)
            retrieved = cache.get("flickr:cars:2")
            self.assertEqual(retrieved, test_data)

            # Test cache clear
            cache.clear()
            self.assertIsNone(cache.get("flickr:cars:2"))


if __name__ == "__main__":
    unittest.main()
