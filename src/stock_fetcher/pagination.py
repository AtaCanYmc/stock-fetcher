import base64
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from .models import StockImage


def encode_cursor(page: int, offset: int = 0) -> str:
    """Encode page and offset into an opaque, deterministic URL-safe cursor string.

    Args:
        page: 1-indexed page number.
        offset: 0-indexed item offset.

    Returns:
        str: Base64-encoded URL-safe cursor.
    """
    safe_page = max(1, int(page))
    safe_offset = max(0, int(offset))
    payload = json.dumps(
        {"page": safe_page, "offset": safe_offset}, separators=(",", ":")
    )
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8").rstrip("=")


def decode_cursor(cursor: Optional[str]) -> Tuple[int, int]:
    """Decode a cursor string into (page, offset).

    Supports standard base64 cursors as well as plain numeric page strings.

    Args:
        cursor: Opaque cursor string or None.

    Returns:
        Tuple[int, int]: Tuple of (page, offset). Defaults to (1, 0) if invalid.
    """
    if not cursor or not isinstance(cursor, str):
        return 1, 0

    clean_cursor = cursor.strip()
    if not clean_cursor or len(clean_cursor) > 1024:
        return 1, 0

    # Handle plain integer page string (e.g. "2" or "p2")
    if clean_cursor.isdigit():
        p = max(1, int(clean_cursor))
        return p, 0
    if clean_cursor.lower().startswith("p") and clean_cursor[1:].isdigit():
        p = max(1, int(clean_cursor[1:]))
        return p, 0

    # Try base64 decoding
    try:
        # Add required padding
        padding = "=" * (-len(clean_cursor) % 4)
        decoded_bytes = base64.urlsafe_b64decode(clean_cursor + padding)
        data = json.loads(decoded_bytes.decode("utf-8"))
        if isinstance(data, dict):
            page = max(1, int(data.get("page", 1)))
            offset = max(0, int(data.get("offset", 0)))
            return page, offset
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        pass

    return 1, 0


def normalize_pagination(
    limit: int,
    page: Optional[int] = None,
    offset: Optional[int] = None,
    cursor: Optional[str] = None,
    max_limit: int = 100,
) -> Tuple[int, int, int]:
    """Normalize and reconcile limit, page, and offset across heterogeneous provider semantics.

    Args:
        limit: Desired number of results.
        page: 1-indexed page number if directly specified.
        offset: 0-indexed item offset if directly specified.
        cursor: Opaque cursor string if provided.
        max_limit: Maximum allowed limit ceiling.

    Returns:
        Tuple[int, int, int]: (clamped_limit, normalized_page, normalized_offset)
    """
    try:
        clamped_limit = max(1, min(int(limit), max_limit))
    except (TypeError, ValueError):
        clamped_limit = 15

    # 1. Cursor takes precedence if provided
    if cursor:
        cur_page, cur_offset = decode_cursor(cursor)
        # If offset was not recorded, derive from page
        if cur_offset == 0 and cur_page > 1:
            cur_offset = (cur_page - 1) * clamped_limit
        return clamped_limit, cur_page, cur_offset

    # 2. Direct offset specified
    if offset is not None:
        try:
            safe_offset = max(0, int(offset))
            derived_page = (safe_offset // clamped_limit) + 1
            return clamped_limit, derived_page, safe_offset
        except (TypeError, ValueError):
            pass

    # 3. Direct page specified
    if page is not None:
        try:
            safe_page = max(1, int(page))
            derived_offset = (safe_page - 1) * clamped_limit
            return clamped_limit, safe_page, derived_offset
        except (TypeError, ValueError):
            pass

    # Default to first page
    return clamped_limit, 1, 0


def build_next_cursor(
    page: int,
    limit: int,
    returned_count: int,
    offset: int = 0,
) -> Optional[str]:
    """Deterministically compute the next cursor, returning None if fewer items than limit were returned."""
    if returned_count < limit:
        return None
    next_page = max(1, page) + 1
    next_offset = max(0, offset) + returned_count
    return encode_cursor(page=next_page, offset=next_offset)


def build_prev_cursor(
    page: int,
    limit: int,
    offset: int = 0,
) -> Optional[str]:
    """Compute previous cursor, returning None if already on the first page."""
    if page <= 1:
        return None
    prev_page = page - 1
    prev_offset = max(0, offset - limit)
    return encode_cursor(page=prev_page, offset=prev_offset)


@dataclass
class PaginationMetadata:
    """Metadata describing the pagination state of a query."""

    page: int
    offset: int
    limit: int
    count: int
    has_more: bool
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PaginatedResult:
    """Container wrapping search results alongside deterministic pagination metadata."""

    items: List[StockImage]
    pagination: PaginationMetadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "pagination": self.pagination.to_dict(),
        }
