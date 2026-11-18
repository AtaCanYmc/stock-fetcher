from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class StockImage(BaseModel):
    """Structured data model representing an image retrieved from a stock photo provider."""

    id: str = Field(
        ..., description="Unique photo identifier within provider namespace"
    )
    source: str = Field(
        ..., description="Source provider identifier (e.g. 'pexels', 'pixabay')"
    )
    url_page: str = Field(
        ..., description="Webpage URL of the photo on the provider platform"
    )
    url_original: str = Field(
        ..., description="Direct URL to the original or high-resolution image file"
    )
    url_thumb: Optional[str] = Field(
        default=None, description="Direct URL to thumbnail preview"
    )
    title: Optional[str] = Field(
        default=None, description="Image title, description, or caption"
    )
    author: Optional[str] = Field(
        default=None, description="Photographer or creator username"
    )
    width: Optional[int] = Field(
        default=None, description="Original image width in pixels"
    )
    height: Optional[int] = Field(
        default=None, description="Original image height in pixels"
    )
    extra: Dict[str, Any] = Field(
        default_factory=dict, description="Raw provider metadata payload"
    )

    def __getitem__(self, item: str) -> Any:
        """Subscript access for backwards compatibility with dictionary interfaces."""
        if hasattr(self, item):
            return getattr(self, item)
        # Compatibility fallback for legacy 'url' key
        if item == "url":
            return self.url_page
        raise KeyError(f"'{self.__class__.__name__}' object has no field '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        """Dictionary-like get method for backwards compatibility."""
        try:
            return self[item]
        except KeyError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        """Export model as a standard dictionary."""
        return self.model_dump()
