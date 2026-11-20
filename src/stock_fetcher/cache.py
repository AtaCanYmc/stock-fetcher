import hashlib
import json
import os
import re
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CacheConfig:
    """Configuration options for response caching."""

    enabled: bool = True
    backend: str = "memory"  # 'memory' or 'disk'
    default_ttl: int = 3600  # Default 1 hour TTL
    cache_dir: Optional[str] = (
        None  # Defaults to ~/.cache/stock-fetcher if backend is 'disk'
    )


class BaseCache(ABC):
    """Abstract base class for response caching implementations."""

    @abstractmethod
    def get(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached records for the given key, or None if missing or expired."""
        pass

    @abstractmethod
    def set(
        self, key: str, data: List[Dict[str, Any]], ttl: Optional[int] = None
    ) -> None:
        """Store records under the given key with an optional TTL in seconds."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Flush all cached records."""
        pass


class MemoryCache(BaseCache):
    """Thread-safe in-memory cache with TTL expiration."""

    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self._store: Dict[str, Tuple[List[Dict[str, Any]], float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[List[Dict[str, Any]]]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            data, expires_at = entry
            if time.time() >= expires_at:
                del self._store[key]
                return None
            return [dict(item) for item in data]

    def set(
        self, key: str, data: List[Dict[str, Any]], ttl: Optional[int] = None
    ) -> None:
        duration = ttl if (ttl is not None and ttl > 0) else self.default_ttl
        expires_at = time.time() + duration
        with self._lock:
            self._store[key] = ([dict(item) for item in data], expires_at)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


class DiskCache(BaseCache):
    """Persistent on-disk cache with TTL expiration."""

    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        if cache_dir:
            self.cache_dir = os.path.abspath(cache_dir)
        else:
            home = os.path.expanduser("~")
            self.cache_dir = os.path.join(home, ".cache", "stock-fetcher")
        os.makedirs(self.cache_dir, exist_ok=True)
        try:
            os.chmod(self.cache_dir, 0o700)
        except OSError:
            pass
        self._lock = threading.Lock()

    def _file_path_for_key(self, key: str) -> str:
        hashed = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed}.json")

    def get(self, key: str) -> Optional[List[Dict[str, Any]]]:
        path = self._file_path_for_key(key)
        if not os.path.exists(path):
            return None

        with self._lock:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                if time.time() >= payload.get("expires_at", 0):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                    return None
                return payload.get("data")
            except (json.JSONDecodeError, OSError):
                return None

    def set(
        self, key: str, data: List[Dict[str, Any]], ttl: Optional[int] = None
    ) -> None:
        duration = ttl if (ttl is not None and ttl > 0) else self.default_ttl
        expires_at = time.time() + duration
        payload = {
            "key": key,
            "expires_at": expires_at,
            "data": [dict(item) for item in data],
        }

        path = self._file_path_for_key(key)
        tmp_path = f"{path}.tmp.{os.getpid()}"

        with self._lock:
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    try:
                        os.chmod(tmp_path, 0o600)
                    except OSError:
                        pass
                    json.dump(payload, f)
                os.replace(tmp_path, path)
            except OSError:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass

    def clear(self) -> None:
        with self._lock:
            if not os.path.exists(self.cache_dir):
                return
            for entry in os.listdir(self.cache_dir):
                if entry.endswith(".json"):
                    try:
                        os.remove(os.path.join(self.cache_dir, entry))
                    except OSError:
                        pass


def build_cache_key(provider: str, term: str, limit: int, page: int = 1) -> str:
    """Generate a deterministic cache key for a search request."""
    base = f"{provider.lower().strip()}:{term.lower().strip()}:{limit}"
    if page and page > 1:
        return f"{base}:p{page}"
    return base


def parse_cache_control_ttl(headers: Any) -> Optional[int]:
    """Parse max-age directive from HTTP response Cache-Control headers."""
    if not headers:
        return None
    # Handle dict or httpx/requests Headers object
    cache_control = headers.get("cache-control") or headers.get("Cache-Control")
    if not cache_control:
        return None

    cc_str = str(cache_control).lower()
    if "no-store" in cc_str:
        return 0

    match = re.search(r"max-age=(\d+)", cc_str)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def get_cache_instance(config: Optional[CacheConfig]) -> Optional[BaseCache]:
    """Instantiate a cache provider based on CacheConfig."""
    if not config or not config.enabled:
        return None
    if config.backend == "disk":
        return DiskCache(cache_dir=config.cache_dir, default_ttl=config.default_ttl)
    return MemoryCache(default_ttl=config.default_ttl)
