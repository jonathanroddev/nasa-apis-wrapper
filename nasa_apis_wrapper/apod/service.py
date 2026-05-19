from typing import List, Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import APOD, APODRequest
from ..utils import obj_dict


class APODService(BaseAPI):
    """Service for the Astronomy Picture of the Day (APOD) API."""

    def get_astronomy_picture_of_day(self, apod_request: Optional[APODRequest] = None) -> APOD:
        """
        Retrieve a single Astronomy Picture of the Day.

        Use this method when querying by ``date`` or with no parameters (returns today's picture).
        For date ranges or random selections, use :meth:`get_astronomy_pictures`.

        Args:
            apod_request: Optional request with ``date`` or ``thumbs`` parameters.
                Do not pass ``start_date``, ``end_date``, or ``count`` — those
                return multiple images and belong in :meth:`get_astronomy_pictures`.

        Returns:
            Single APOD object.

        Raises:
            NasaAPIException: If the API request fails.
        """
        return self._parse_one(
            "/planetary/apod",
            APOD,
            params=obj_dict(apod_request) if apod_request else None,
        )

    def get_astronomy_pictures(self, apod_request: APODRequest) -> List[APOD]:
        """
        Retrieve multiple Astronomy Pictures of the Day.

        Use this method when the request includes ``start_date``/``end_date``
        (date range) or ``count`` (random selection), as the API returns a list
        in those cases.

        Args:
            apod_request: Request with ``start_date``/``end_date`` or ``count``.

        Returns:
            List of APOD objects.

        Raises:
            NasaAPIException: If the API request fails.
        """
        return self._parse_list(
            "/planetary/apod",
            APOD,
            params=obj_dict(apod_request),
        )
