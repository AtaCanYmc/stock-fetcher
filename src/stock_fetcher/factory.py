from typing import Dict, Type
from .base import BaseFetcher
from .exceptions import ProviderNotFoundError
from .clients.pexels import PexelsClient
from .clients.pixabay import PixabayClient
from .clients.unsplash import UnsplashClient
from .clients.flickr import FlickrClient


class ClientFactory:
    """Factory for creating and managing fetcher clients."""

    _clients: Dict[str, Type[BaseFetcher]] = {
        "pexels": PexelsClient,
        "pixabay": PixabayClient,
        "unsplash": UnsplashClient,
        "flickr": FlickrClient,
    }

    @classmethod
    def get(cls, provider: str, api_key: str = "") -> BaseFetcher:
        """
        Get an instance of a provider client.

        Args:
            provider (str): The name of the provider (e.g., 'pixabay').
            api_key (str): The API key for the provider.

        Returns:
            BaseFetcher: An instance of the requested client.

        Raises:
            ProviderNotFoundError: If the provider is not supported.
        """
        provider_lower = provider.lower()
        if provider_lower not in cls._clients:
            raise ProviderNotFoundError(
                f"Provider '{provider}' is not supported. "
                f"Available providers: {list(cls._clients.keys())}"
            )

        return cls._clients[provider_lower](api_key=api_key)
