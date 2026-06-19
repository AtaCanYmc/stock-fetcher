<p align="center">
  <img src="assets/logo.png" alt="Stock Fetcher Logo" width="200">
</p>

# Stock Fetcher

Stock Fetcher is a standalone, lightweight Python library for fetching copyright-free images and photos from various popular sources such as Pexels, Pixabay, Unsplash, and Flickr.

Built with a clean architecture and type hints, it makes retrieving high-quality stock images across multiple providers simple and consistent.

## Features

- **Unified Interface:** Fetch images using a consistent API regardless of the backend source.
- **Multiple Providers:** Out-of-the-box support for Pexels, Pixabay, Unsplash, and Flickr.
- **Type Hinting:** Fully type-hinted for better IDE integration.
- **Error Handling:** Standardized `FetcherError` wrapper for easy debugging and exception catching.

## Installation

You can install the package directly from the source directory:

```bash
pip install .
```

## Quick Start

Import the client for the platform you want to use. You must provide an API key for Pexels, Pixabay, and Unsplash. (Flickr uses a custom scrapper and does not require an API key in this implementation).

### Using Pixabay

```python
from stock_fetcher import PixabayClient, FetcherError

client = PixabayClient(api_key="YOUR_PIXABAY_API_KEY")

try:
    images = client.search_images(query="nature", per_page=5)
    for img in images:
        print(f"[{img['source']}] Original URL: {img['url_original']}")
except FetcherError as e:
    print(f"Error: {e}")
```

### Using Unsplash

```python
from stock_fetcher import UnsplashClient, FetcherError

client = UnsplashClient(api_key="YOUR_UNSPLASH_ACCESS_KEY")

try:
    images = client.search_images(query="architecture", per_page=3)
    for img in images:
        print(f"[{img['source']}] ID: {img['id']} - URL: {img['url_original']}")
except FetcherError as e:
    print(f"Error: {e}")
```

### Using Pexels

```python
from stock_fetcher import PexelsClient

client = PexelsClient(api_key="YOUR_PEXELS_API_KEY")
images = client.search_images(query="technology", per_page=3)
```

### Using Flickr

```python
from stock_fetcher import FlickrClient

client = FlickrClient() # No API key required for the scrapper
images = client.search_images(query="vintage cars", per_page=5)
```

## Error Handling

The library provides a custom `FetcherError` exception to handle API failures uniformly.

```python
from stock_fetcher import PexelsClient, FetcherError

client = PexelsClient(api_key="INVALID_KEY")

try:
    client.search_images("test")
except FetcherError as e:
    print(f"A fetching error occurred: {e}")
```