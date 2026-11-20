import asyncio
import random
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable, Coroutine, Dict, Optional

import httpx

from .exceptions import RateLimitExceededError


@dataclass
class RateLimitInfo:
    """Parsed rate limit status extracted from HTTP headers."""

    remaining: Optional[int] = None
    limit: Optional[int] = None
    reset_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_rate_limit_headers(headers: Any) -> RateLimitInfo:
    """Extract standard rate limit and backoff headers case-insensitively.

    Supports:
        - X-RateLimit-Remaining / X-Ratelimit-Remaining / RateLimit-Remaining
        - X-RateLimit-Limit / X-Ratelimit-Limit / RateLimit-Limit
        - Retry-After (seconds or delta)
        - X-RateLimit-Reset / X-Ratelimit-Reset (seconds or epoch timestamp)
    """
    if not headers or not hasattr(headers, "get"):
        return RateLimitInfo()

    def _get_val(*keys: str) -> Optional[Any]:
        for k in keys:
            v = headers.get(k)
            if v is not None:
                return v
        if hasattr(headers, "items"):
            key_set = {k.lower() for k in keys}
            for hk, hv in headers.items():
                if str(hk).lower() in key_set:
                    return hv
        return None

    remaining: Optional[int] = None
    raw_rem = _get_val(
        "x-ratelimit-remaining",
        "x-rate-limit-remaining",
        "ratelimit-remaining",
    )
    if raw_rem is not None:
        try:
            remaining = int(raw_rem)
        except (ValueError, TypeError):
            pass

    limit: Optional[int] = None
    raw_lim = _get_val(
        "x-ratelimit-limit",
        "x-rate-limit-limit",
        "ratelimit-limit",
    )
    if raw_lim is not None:
        try:
            limit = int(raw_lim)
        except (ValueError, TypeError):
            pass

    reset_seconds: Optional[float] = None
    raw_retry = _get_val("retry-after")
    if raw_retry is not None:
        try:
            reset_seconds = max(0.0, float(raw_retry))
        except (ValueError, TypeError):
            pass

    if reset_seconds is None:
        raw_reset = _get_val(
            "x-ratelimit-reset",
            "x-rate-limit-reset",
            "ratelimit-reset",
        )
        if raw_reset is not None:
            try:
                num = float(raw_reset)
                # If Unix epoch timestamp (> 1e9), calculate delta from now
                if num > 1_000_000_000:
                    reset_seconds = max(0.0, num - time.time())
                else:
                    reset_seconds = max(0.0, num)
            except (ValueError, TypeError):
                pass

    if reset_seconds is not None:
        reset_seconds = max(0.0, min(reset_seconds, 86400.0))

    return RateLimitInfo(
        remaining=remaining,
        limit=limit,
        reset_seconds=reset_seconds,
    )


class AdaptiveRateLimiter:
    """Manages adaptive throttling, rate limit header tracking, and exponential backoff."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        max_retries: int = 3,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self._provider_limits: Dict[str, RateLimitInfo] = {}

    def get_rate_limit(self, provider: str) -> Optional[RateLimitInfo]:
        """Return the most recent rate limit information for a given provider."""
        return self._provider_limits.get(provider.lower())

    def record_response(self, provider: str, response: httpx.Response) -> RateLimitInfo:
        """Parse and store rate limit status from response headers."""
        info = parse_rate_limit_headers(response.headers)
        self._provider_limits[provider.lower()] = info
        return info

    def calculate_backoff(
        self,
        attempt: int,
        response: Optional[httpx.Response] = None,
    ) -> float:
        """Determine backoff duration in seconds using Retry-After header or exponential backoff with jitter."""
        if response is not None:
            info = parse_rate_limit_headers(response.headers)
            if info.reset_seconds is not None and info.reset_seconds > 0:
                return min(info.reset_seconds, self.max_delay)

        # Exponential backoff: base * 2^attempt + jitter
        jitter = random.uniform(0.05, 0.25)
        backoff = self.base_delay * (2**attempt) + jitter
        return min(backoff, self.max_delay)

    def get_pacing_delay(self, provider: str) -> float:
        """Calculate a proactive pacing delay if the provider is nearing quota exhaustion (remaining <= 1)."""
        info = self.get_rate_limit(provider)
        if not info:
            return 0.0

        if info.remaining is not None and info.remaining <= 1:
            if info.reset_seconds is not None and 0.0 < info.reset_seconds <= 3.0:
                return min(info.reset_seconds, 1.0)
            return 0.5  # Safe pacing pause for burst protection
        return 0.0

    def execute_sync(
        self,
        fetch_func: Callable[[], httpx.Response],
        provider: str,
        mask_error_func: Optional[Callable[[Exception], str]] = None,
    ) -> httpx.Response:
        """Execute a synchronous HTTP request with proactive pacing and exponential backoff on 429."""
        pacing = self.get_pacing_delay(provider)
        if pacing > 0:
            time.sleep(pacing)

        last_response: Optional[httpx.Response] = None

        for attempt in range(self.max_retries + 1):
            response = fetch_func()
            last_response = response
            self.record_response(provider, response)

            # Retry on 429 (Too Many Requests) or transient 503 (Service Unavailable)
            if response.status_code in (429, 503):
                if attempt < self.max_retries:
                    delay = self.calculate_backoff(attempt, response)
                    time.sleep(delay)
                    continue
                else:
                    info = self.get_rate_limit(provider)
                    retry_sec = info.reset_seconds if info else None
                    msg = (
                        f"Rate limit exceeded for provider '{provider}' "
                        f"(status {response.status_code}). Exhausted {self.max_retries} retries."
                    )
                    if mask_error_func:
                        msg = mask_error_func(Exception(msg))
                    raise RateLimitExceededError(
                        msg, retry_after=retry_sec, provider=provider
                    )

            return response

        return last_response  # Fallback

    async def execute_async(
        self,
        afetch_func: Callable[[], Coroutine[Any, Any, httpx.Response]],
        provider: str,
        mask_error_func: Optional[Callable[[Exception], str]] = None,
    ) -> httpx.Response:
        """Execute an asynchronous HTTP request with proactive pacing and exponential backoff on 429."""
        pacing = self.get_pacing_delay(provider)
        if pacing > 0:
            await asyncio.sleep(pacing)

        last_response: Optional[httpx.Response] = None

        for attempt in range(self.max_retries + 1):
            response = await afetch_func()
            last_response = response
            self.record_response(provider, response)

            if response.status_code in (429, 503):
                if attempt < self.max_retries:
                    delay = self.calculate_backoff(attempt, response)
                    await asyncio.sleep(delay)
                    continue
                else:
                    info = self.get_rate_limit(provider)
                    retry_sec = info.reset_seconds if info else None
                    msg = (
                        f"Rate limit exceeded for provider '{provider}' "
                        f"(status {response.status_code}). Exhausted {self.max_retries} retries."
                    )
                    if mask_error_func:
                        msg = mask_error_func(Exception(msg))
                    raise RateLimitExceededError(
                        msg, retry_after=retry_sec, provider=provider
                    )

            return response

        return last_response  # Fallback


# Global default rate limiter instance for shared state across client queries
default_rate_limiter = AdaptiveRateLimiter()
