import datetime
from typing import List, Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    EPICCollection,
    EPICImageFormat,
    EPICImage,
    EPICDateItem,
)


class EPICService(BaseAPI):
    """
    Service for the Earth Polychromatic Imaging Camera (EPIC) API.

    Provides access to full-disc imagery of the Earth taken from the DSCOVR
    spacecraft at the L1 Lagrange point. No API key required.

    Available collections: ``"natural"``, ``"enhanced"``, ``"aerosol"``, ``"cloud"``.
    """

    _ARCHIVE = "https://epic.gsfc.nasa.gov/archive"

    def __init__(self):
        super().__init__()  # EPIC does not require an API key
        self.host = "https://epic.gsfc.nasa.gov/api"

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------

    def images(
        self,
        collection: EPICCollection = "natural",
        date: Optional[datetime.date] = None,
    ) -> List[EPICImage]:
        """
        Retrieve EPIC images for a given collection and date.

        Args:
            collection: Image collection. One of ``"natural"``, ``"enhanced"``,
                ``"aerosol"``, or ``"cloud"``. Defaults to ``"natural"``.
            date: Date to retrieve images for. If omitted, returns the most
                recently available images.

        Returns:
            List of EPICImage objects with metadata and positional data.

        Raises:
            NasaAPIException: If the request fails.
        """
        endpoint = f"/{collection}"
        if date:
            endpoint += f"/date/{date.strftime('%Y-%m-%d')}"
        return self._parse_list(endpoint, EPICImage)

    # ------------------------------------------------------------------
    # Dates
    # ------------------------------------------------------------------

    def available_dates(self, collection: EPICCollection = "natural") -> List[str]:
        """
        Retrieve the list of dates that have available images.

        Args:
            collection: Image collection. Defaults to ``"natural"``.

        Returns:
            List of date strings in ``"YYYY-MM-DD"`` format.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self.get_request(f"/{collection}/available")

    def all_dates(self, collection: EPICCollection = "natural") -> List[EPICDateItem]:
        """
        Retrieve the list of dates that have available images as objects.

        Equivalent to :meth:`available_dates` but returns a list of
        :class:`EPICDateItem` objects instead of plain strings.

        Args:
            collection: Image collection. Defaults to ``"natural"``.

        Returns:
            List of EPICDateItem objects, each with a ``date`` field.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self._parse_list(f"/{collection}/all", EPICDateItem)

    # ------------------------------------------------------------------
    # Image URL builder
    # ------------------------------------------------------------------

    def image_url(
        self,
        image: EPICImage,
        collection: EPICCollection = "natural",
        fmt: EPICImageFormat = "png",
    ) -> str:
        """
        Build the archive URL for a given image.

        Args:
            image: An EPICImage returned by :meth:`images`.
            collection: Collection the image belongs to. Defaults to ``"natural"``.
            fmt: Image format. One of ``"png"`` (2048×2048), ``"jpg"``
                (reduced resolution), or ``"thumbs"`` (thumbnail). Defaults to ``"png"``.

        Returns:
            Full URL to the image file.

        Example::

            images = service.images("natural")
            url = service.image_url(images[0], "natural", fmt="jpg")
        """
        dt = image.date
        ext = "jpg" if fmt == "thumbs" else fmt
        return (
            f"{self._ARCHIVE}/{collection}"
            f"/{dt.strftime('%Y')}/{dt.strftime('%m')}/{dt.strftime('%d')}"
            f"/{fmt}/{image.image}.{ext}"
        )
