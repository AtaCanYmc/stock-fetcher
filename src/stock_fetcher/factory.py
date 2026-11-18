import asyncio
import os
from typing import Dict, List, Optional, Type

from .base import BaseFetcher
from .cache import BaseCache
from .clients.flickr import FlickrClient
from .clients.pexels import PexelsClient
from .clients.pixabay import PixabayClient
from .clients.unsplash import UnsplashClient
from .exceptions import AuthenticationError, ProviderNotFoundError
from .models import StockImage


class ClientFactory:
    """Factory for creating and managing fetcher clients with sync and async support."""

    _clients: Dict[str, Type[BaseFetcher]] = {
        "pexels": PexelsClient,
        "pixabay": PixabayClient,
        "unsplash": UnsplashClient,
        "flickr": FlickrClient,
    }

    _env_keys: Dict[str, str] = {
        "pexels": "PEXELS_API_KEY",
        "pixabay": "PIXABAY_API_KEY",
        "unsplash": "UNSPLASH_API_KEY",
        "flickr": "",
    }

    @classmethod
    def get(
        cls,
        provider: str,
        api_key: str = "",
        cache: Optional[BaseCache] = None,
    ) -> BaseFetcher:
        """Get an instance of a provider client.

        Args:
            provider: The name of the provider (e.g. 'pixabay', 'pexels').
            api_key: The API key for the provider.
            cache: Optional response cache backend (MemoryCache or DiskCache).

        Returns:
            BaseFetcher: Client instance implementing both search() and asearch().

        Raises:
            ProviderNotFoundError: If the provider is unsupported.
        """
        provider_lower = provider.lower().strip()
        if provider_lower not in cls._clients:
            raise ProviderNotFoundError(
                f"Provider '{provider}' is not supported. "
                f"Available providers: {list(cls._clients.keys())}"
            )

        return cls._clients[provider_lower](api_key=api_key, cache=cache)

    @classmethod
    async def asearch_all(
        cls,
        term: str,
        limit: int = 5,
        api_keys: Optional[Dict[str, str]] = None,
        cache: Optional[BaseCache] = None,
        providers: Optional[List[str]] = None,
    ) -> Dict[str, List[StockImage]]:
        """Concurrently search across multiple providers using asyncio.gather.

        Args:
            term: Search query term.
            limit: Maximum photos to return per provider.
            api_keys: Optional mapping of provider names to API keys.
            cache: Optional shared cache backend.
            providers: List of providers to query. Defaults to all registered providers.

        Returns:
            Dict[str, List[StockImage]]: Mapping of provider names to retrieved image models.
        """
        keys_map = api_keys or {}
        targets = providers or list(cls._clients.keys())

        async def _query_single(p_name: str) -> tuple[str, List[StockImage]]:
            p_clean = p_name.lower().strip()
            if p_clean not in cls._clients:
                return p_clean, []

            api_key = keys_map.get(p_clean) or os.getenv(
                cls._env_keys.get(p_clean, ""), ""
            )
            try:
                client = cls.get(p_clean, api_key=api_key, cache=cache)
                results = await client.asearch(term, limit=limit)
                return p_clean, results
            except (AuthenticationError, Exception):
                # Suppress missing credentials or timeouts in multi-provider concurrent queries
                return p_clean, []

        tasks = [_query_single(p) for p in targets]
        pairs = await asyncio.gather(*tasks)
        return {p: res for p, res in pairs if res}
