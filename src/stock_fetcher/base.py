import re
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple
from urllib.parse import quote, quote_plus

import httpx

from .cache import BaseCache, build_cache_key, parse_cache_control_ttl
from .models import StockImage
from .pagination import (
    PaginatedResult,
    PaginationMetadata,
    build_next_cursor,
    build_prev_cursor,
    normalize_pagination,
)
from .rate_limit import (
    AdaptiveRateLimiter,
    RateLimitInfo,
    default_rate_limiter,
)


class BaseFetcher(ABC):
    """Abstract base class for all image fetcher clients."""

    def __init__(
        self,
        api_key: str = "",
        cache: Optional[BaseCache] = None,
        rate_limiter: Optional[AdaptiveRateLimiter] = None,
    ):
        self.api_key = api_key.strip() if api_key else ""
        self.cache = cache
        self.rate_limiter = rate_limiter or default_rate_limiter

    @property
    @abstractmethod
    def name(self) -> str:
        """Normalized lowercase provider name."""
        pass

    @property
    def rate_limit_info(self) -> Optional[RateLimitInfo]:
        """Return the most recently parsed rate limit information for this provider."""
        return self.rate_limiter.get_rate_limit(self.name)

    @staticmethod
    def sanitize_search_params(
        term: str, limit: int, max_limit: int = 100
    ) -> Tuple[str, int]:
        """Validate search query and enforce safe pagination bounds.

        Args:
            term: The search query string.
            limit: Requested number of items.
            max_limit: Upper bound ceiling to prevent rate limit abuse.

        Returns:
            Tuple[str, int]: Cleaned term and clamped limit.

        Raises:
            ValueError: If term is empty or invalid.
        """
        if not isinstance(term, str) or not term.strip():
            raise ValueError("Search term cannot be empty.")

        clean_term = term.replace("\0", "").strip()[:500]
        if not clean_term:
            raise ValueError("Search term cannot be empty.")

        try:
            clamped_limit = max(1, min(int(limit), max_limit))
        except (TypeError, ValueError):
            clamped_limit = 15

        return clean_term, clamped_limit

    def normalize_pagination(
        self,
        limit: int,
        page: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
        max_limit: int = 100,
    ) -> Tuple[int, int, int]:
        """Reconcile and normalize pagination parameters across providers.

        Returns:
            Tuple[int, int, int]: (clamped_limit, normalized_page, normalized_offset)
        """
        return normalize_pagination(
            limit=limit,
            page=page,
            offset=offset,
            cursor=cursor,
            max_limit=max_limit,
        )

    def _mask_error(self, exc: Exception) -> str:
        """Mask credentials from exception messages before surfacing to callers."""
        err_msg = str(exc)
        if not self.api_key:
            return err_msg

        # Raw key
        err_msg = err_msg.replace(self.api_key, "***")

        # Percent-encoded variants
        try:
            q1 = quote(self.api_key)
            if q1 != self.api_key:
                err_msg = err_msg.replace(q1, "***")
            q2 = quote_plus(self.api_key)
            if q2 != self.api_key and q2 != q1:
                err_msg = err_msg.replace(q2, "***")
        except Exception:
            pass

        # Regex masking for common authentication parameters in URLs and headers
        err_msg = re.sub(
            r"(key|client_id|access_key|token|api_key)=([a-zA-Z0-9_\-\.]+)",
            r"\1=***",
            err_msg,
            flags=re.IGNORECASE,
        )
        err_msg = re.sub(
            r"(Bearer\s+)([a-zA-Z0-9_\-\.]+)",
            r"\1***",
            err_msg,
            flags=re.IGNORECASE,
        )
        return err_msg

    def _get_cached_results(
        self, term: str, limit: int, page: int = 1
    ) -> Optional[List[StockImage]]:
        """Retrieve cached results if cache is configured and entry is unexpired."""
        if not self.cache:
            return None
        key = build_cache_key(self.name, term, limit, page=page)
        cached_data = self.cache.get(key)
        if cached_data is not None:
            return [StockImage(**item) for item in cached_data]
        return None

    def _save_cached_results(
        self,
        term: str,
        limit: int,
        results: List[StockImage],
        headers: Any = None,
        page: int = 1,
    ) -> None:
        """Store results into cache honoring upstream Cache-Control headers."""
        if not self.cache:
            return
        key = build_cache_key(self.name, term, limit, page=page)
        ttl = parse_cache_control_ttl(headers)
        data = [img.to_dict() for img in results]
        self.cache.set(key, data, ttl=ttl)

    def _request_with_retry(
        self,
        client: httpx.Client,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a synchronous HTTP request with adaptive pacing and exponential backoff on 429."""
        if method.upper() == "GET":
            fetcher = lambda: client.get(url, **kwargs)  # noqa: E731
        else:
            fetcher = lambda: client.request(method, url, **kwargs)  # noqa: E731

        return self.rate_limiter.execute_sync(
            fetch_func=fetcher,
            provider=self.name,
            mask_error_func=self._mask_error,
        )

    async def _arequest_with_retry(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute an asynchronous HTTP request with adaptive pacing and exponential backoff on 429."""
        if method.upper() == "GET":
            afetcher = lambda: client.get(url, **kwargs)  # noqa: E731
        else:
            afetcher = lambda: client.request(method, url, **kwargs)  # noqa: E731

        return await self.rate_limiter.execute_async(
            afetch_func=afetcher,
            provider=self.name,
            mask_error_func=self._mask_error,
        )

    @abstractmethod
    def search(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> List[StockImage]:
        """Synchronous search for images based on a search term and pagination cursor."""
        pass

    @abstractmethod
    async def asearch(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> List[StockImage]:
        """Asynchronous non-blocking search for images using httpx."""
        pass

    def search_paginated(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> PaginatedResult:
        """Synchronous search returning a container with deterministic pagination cursors."""
        safe_limit, norm_page, norm_offset = self.normalize_pagination(
            limit=limit, page=page, cursor=cursor
        )
        items = self.search(term=term, limit=safe_limit, page=norm_page, cursor=cursor)
        has_more = len(items) >= safe_limit
        next_c = build_next_cursor(
            page=norm_page,
            limit=safe_limit,
            returned_count=len(items),
            offset=norm_offset,
        )
        prev_c = build_prev_cursor(page=norm_page, limit=safe_limit, offset=norm_offset)

        metadata = PaginationMetadata(
            page=norm_page,
            offset=norm_offset,
            limit=safe_limit,
            count=len(items),
            has_more=has_more,
            next_cursor=next_c,
            prev_cursor=prev_c,
        )
        return PaginatedResult(items=items, pagination=metadata)

    async def asearch_paginated(
        self,
        term: str,
        limit: int = 15,
        page: int = 1,
        cursor: Optional[str] = None,
    ) -> PaginatedResult:
        """Asynchronous search returning a container with deterministic pagination cursors."""
        safe_limit, norm_page, norm_offset = self.normalize_pagination(
            limit=limit, page=page, cursor=cursor
        )
        items = await self.asearch(
            term=term, limit=safe_limit, page=norm_page, cursor=cursor
        )
        has_more = len(items) >= safe_limit
        next_c = build_next_cursor(
            page=norm_page,
            limit=safe_limit,
            returned_count=len(items),
            offset=norm_offset,
        )
        prev_c = build_prev_cursor(page=norm_page, limit=safe_limit, offset=norm_offset)

        metadata = PaginationMetadata(
            page=norm_page,
            offset=norm_offset,
            limit=safe_limit,
            count=len(items),
            has_more=has_more,
            next_cursor=next_c,
            prev_cursor=prev_c,
        )
        return PaginatedResult(items=items, pagination=metadata)
