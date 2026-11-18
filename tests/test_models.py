import unittest

from stock_fetcher.models import StockImage


class StockImageModelTest(unittest.TestCase):
    def test_model_fields_and_subscript(self):
        img = StockImage(
            id="12345",
            source="pixabay",
            url_page="https://pixabay.com/photos/mountain-12345/",
            url_original="https://pixabay.com/get/12345.jpg",
            url_thumb="https://pixabay.com/get/12345_thumb.jpg",
            title="Alpine Mountain",
            author="photographer_joe",
            width=1920,
            height=1080,
            extra={"views": 500},
        )

        # Attribute access
        self.assertEqual(img.id, "12345")
        self.assertEqual(img.source, "pixabay")
        self.assertEqual(img.url_original, "https://pixabay.com/get/12345.jpg")
        self.assertEqual(img.width, 1920)

        # Subscript access (dict compatibility)
        self.assertEqual(img["id"], "12345")
        self.assertEqual(img["source"], "pixabay")
        self.assertEqual(img["url_original"], "https://pixabay.com/get/12345.jpg")
        self.assertEqual(img["url"], "https://pixabay.com/photos/mountain-12345/")

        # .get() access
        self.assertEqual(img.get("title"), "Alpine Mountain")
        self.assertEqual(img.get("nonexistent", "default_val"), "default_val")

        # .to_dict()
        data = img.to_dict()
        self.assertEqual(data["id"], "12345")
        self.assertEqual(data["width"], 1920)


if __name__ == "__main__":
    unittest.main()
