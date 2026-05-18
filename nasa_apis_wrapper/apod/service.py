from typing import Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import APOD, APODRequest
from ..utils import obj_dict


class APODService(BaseAPI):
    """Service for the Astronomy Picture of the Day (APOD) API."""

    def get_astronomy_picture_of_day(self, apod_request: Optional[APODRequest] = None) -> APOD:
        """
        Retrieve the Astronomy Picture of the Day.

        Args:
            apod_request: Optional filters (date, date range, random count, etc.).
                If omitted, returns today's picture.

        Returns:
            APOD object with the image URL, title, explanation, and metadata.

        Raises:
            NasaAPIException: If the API request fails.
        """
        return self._parse_one(
            "/planetary/apod",
            APOD,
            params=obj_dict(apod_request) if apod_request else None,
        )
