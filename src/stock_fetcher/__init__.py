from .base import BaseFetcher
from .cache import BaseCache, CacheConfig, DiskCache, MemoryCache
from .clients.flickr import FlickrClient
from .clients.openverse import OpenverseClient
from .clients.pexels import PexelsClient
from .clients.pixabay import PixabayClient
from .clients.unsplash import UnsplashClient
from .clients.wikimedia import WikimediaClient
from .exceptions import (
    APIConnectionError,
    AuthenticationError,
    ProviderNotFoundError,
    RateLimitExceededError,
    StockFetcherError,
)
from .factory import ClientFactory
from .models import StockImage
from .pagination import (
    PaginatedResult,
    PaginationMetadata,
    decode_cursor,
    encode_cursor,
    normalize_pagination,
)
from .rate_limit import (
    AdaptiveRateLimiter,
    RateLimitInfo,
)

__version__ = "0.4.0"

__all__ = [
    "StockImage",
    "BaseFetcher",
    "ClientFactory",
    "FlickrClient",
    "OpenverseClient",
    "PexelsClient",
    "PixabayClient",
    "UnsplashClient",
    "WikimediaClient",
    "CacheConfig",
    "BaseCache",
    "MemoryCache",
    "DiskCache",
    "PaginatedResult",
    "PaginationMetadata",
    "encode_cursor",
    "decode_cursor",
    "normalize_pagination",
    "RateLimitInfo",
    "AdaptiveRateLimiter",
    "StockFetcherError",
    "APIConnectionError",
    "RateLimitExceededError",
    "AuthenticationError",
    "ProviderNotFoundError",
    "__version__",
]
