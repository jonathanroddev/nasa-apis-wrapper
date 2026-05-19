import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


MediaType = Literal["image", "video", "audio"]


# ---------------------------------------------------------------------------
# Search request
# ---------------------------------------------------------------------------

class ImageLibrarySearchRequest(BaseModel):
    """
    Query parameters for ``GET /search`` and ``GET /album/{album_name}``.

    At least one field must be provided for ``/search``. All fields are
    optional and combinable. ``media_type`` accepts comma-separated values
    to search multiple types at once (e.g. ``"image,video"``).
    """
    q: Optional[str] = None
    center: Optional[str] = None
    description: Optional[str] = None
    description_508: Optional[str] = None
    keywords: Optional[str] = None
    location: Optional[str] = None
    media_type: Optional[str] = None        # "image" | "video" | "audio" or combinations
    nasa_id: Optional[str] = None
    photographer: Optional[str] = None
    secondary_creator: Optional[str] = None
    title: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


# ---------------------------------------------------------------------------
# Search response models
# ---------------------------------------------------------------------------

class MediaData(BaseModel):
    """Metadata for a single NASA media asset."""
    nasa_id: str
    title: str
    media_type: MediaType
    date_created: datetime.datetime
    center: str
    description: str
    keywords: List[str] = []
    description_508: Optional[str] = None
    photographer: Optional[str] = None
    secondary_creator: Optional[str] = None
    location: Optional[str] = None
    album: Optional[List[str]] = None


class SearchItemLink(BaseModel):
    """
    A rendition or related file linked from a search result.

    ``rel`` values:
    - ``"preview"`` — thumbnail (~thumb.jpg)
    - ``"alternate"`` — reduced-size renditions (large, medium, small)
    - ``"canonical"`` — original full-resolution file
    - ``"captions"`` — SRT subtitle file (video only; no ``render`` field)
    """
    href: str
    rel: str
    render: Optional[str] = None           # "image"; absent for "captions"
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None             # bytes


class SearchItem(BaseModel):
    """
    A single result from ``/search`` or ``/album``.

    ``data`` always contains exactly one element. ``links`` is absent for
    audio assets.
    """
    href: str                               # URL to the collection.json manifest
    data: List[MediaData]
    links: Optional[List[SearchItemLink]] = None

    @property
    def metadata(self) -> MediaData:
        """Convenience accessor for the single MediaData element."""
        return self.data[0]

    @property
    def thumbnail(self) -> Optional[str]:
        """URL of the preview thumbnail, or None for audio assets."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "preview":
                return link.href
        return None


class CollectionMetadata(BaseModel):
    total_hits: int


class CollectionLink(BaseModel):
    """Pagination link (next / previous page)."""
    rel: str        # "next" | "prev"
    prompt: str     # "Next" | "Previous"
    href: str


class SearchCollection(BaseModel):
    version: str
    href: str
    items: List[SearchItem]
    metadata: CollectionMetadata
    links: Optional[List[CollectionLink]] = None

    @property
    def next_page(self) -> Optional[str]:
        """URL of the next results page, or None if on the last page."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "next":
                return link.href
        return None

    @property
    def prev_page(self) -> Optional[str]:
        """URL of the previous results page, or None if on the first page."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "prev":
                return link.href
        return None


class SearchResponse(BaseModel):
    """Response from ``GET /search`` and ``GET /album/{album_name}``."""
    collection: SearchCollection


# ---------------------------------------------------------------------------
# Asset manifest response
# ---------------------------------------------------------------------------

class AssetItem(BaseModel):
    """A single rendition entry from ``GET /asset/{nasa_id}``."""
    href: str       # direct CDN URL to the file


class AssetCollection(BaseModel):
    version: str
    href: str
    items: List[AssetItem]


class AssetResponse(BaseModel):
    """
    Response from ``GET /asset/{nasa_id}``.

    ``collection.items`` lists all available renditions (original, large,
    medium, small, thumb for images; original and compressed variants for
    video/audio; plus ``metadata.json`` and captions where applicable).
    """
    collection: AssetCollection

    @property
    def urls(self) -> List[str]:
        """All rendition URLs as a flat list."""
        return [item.href for item in self.collection.items]


# ---------------------------------------------------------------------------
# Location response (metadata + captions)
# ---------------------------------------------------------------------------

class LocationResponse(BaseModel):
    """Response from ``GET /metadata/{nasa_id}`` and ``GET /captions/{nasa_id}``."""
    location: str
