from typing import Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    ImageLibrarySearchRequest,
    SearchResponse,
    AssetResponse,
    LocationResponse,
)
from ..utils import obj_dict


class ImageLibraryService(BaseAPI):
    """
    Service for the NASA Image and Video Library API.

    Provides access to NASA's public archive of images, videos, and audio
    recordings. No API key required.

    Typical workflow::

        service = ImageLibraryService()

        # 1. Search for content
        results = service.search(ImageLibrarySearchRequest(q="Apollo 11", media_type="image"))

        # 2. Get a specific item's metadata
        item = results.collection.items[0]
        print(item.metadata.title)
        print(item.thumbnail)          # quick preview URL

        # 3. Get all renditions for download
        asset = service.asset(item.metadata.nasa_id)
        print(asset.urls)              # list of all file URLs
    """

    def __init__(self):
        super().__init__()  # Image Library does not require an API key
        self.host = "https://images-api.nasa.gov"

    def search(
        self, request: Optional[ImageLibrarySearchRequest] = None
    ) -> SearchResponse:
        """
        Search the NASA Image and Video Library.

        At least one field in ``request`` must be set. All fields are optional
        and combinable. Results are paginated (default 10 per page).

        Args:
            request: Search parameters. Use ``q`` for free-text search,
                ``media_type`` to restrict to images/video/audio, ``year_start``
                and ``year_end`` for date ranges, etc.

        Returns:
            SearchResponse with matching items and pagination metadata.
            Use ``collection.metadata.total_hits`` for the total result count
            and ``collection.next_page`` to navigate to the next page.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request(
            "/search",
            params=obj_dict(request) if request else None,
        )
        return SearchResponse(**data)

    def asset(self, nasa_id: str) -> AssetResponse:
        """
        Retrieve all available renditions for a given asset.

        Args:
            nasa_id: NASA asset identifier (e.g. ``"as11-40-5931"``).

        Returns:
            AssetResponse listing all rendition URLs (original, large, medium,
            small, thumb for images; video/audio variants; metadata.json; SRT).
            Use ``.urls`` for a flat list of all file URLs.

        Raises:
            NasaAPIException: If the asset is not found or the request fails.
        """
        data = self.get_request(f"/asset/{nasa_id}")
        return AssetResponse(**data)

    def metadata(self, nasa_id: str) -> str:
        """
        Get the URL of the XMP/EXIF metadata file for an asset.

        Args:
            nasa_id: NASA asset identifier.

        Returns:
            URL string pointing to the ``metadata.json`` file on the CDN.

        Raises:
            NasaAPIException: If the asset is not found or the request fails.
        """
        data = self.get_request(f"/metadata/{nasa_id}")
        return LocationResponse(**data).location

    def captions(self, nasa_id: str) -> str:
        """
        Get the URL of the SRT subtitle file for a video asset.

        Args:
            nasa_id: NASA video asset identifier.

        Returns:
            URL string pointing to the ``.srt`` captions file on the CDN.

        Raises:
            NasaAPIException: If the asset is not found or the request fails.
        """
        data = self.get_request(f"/captions/{nasa_id}")
        return LocationResponse(**data).location

    def album(
        self,
        album_name: str,
        page: Optional[int] = None,
    ) -> SearchResponse:
        """
        Retrieve all assets belonging to a named album.

        Args:
            album_name: Album name, case-sensitive (e.g. ``"Apollo-at-50"``).
            page: Page number (1-based). Omit for the first page.

        Returns:
            SearchResponse with the same structure as :meth:`search`.

        Raises:
            NasaAPIException: If the album is not found or the request fails.
        """
        params = {"page": page} if page else None
        data = self.get_request(f"/album/{album_name}", params=params)
        return SearchResponse(**data)
