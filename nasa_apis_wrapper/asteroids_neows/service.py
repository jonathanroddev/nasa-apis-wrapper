from typing import Optional, Union

from nasa_apis_wrapper.base import BaseAPI
from .models import NeoFeed, NeoFeedRequest, NearEarthObjectItem, NeoBrowse, Pagination
from ..utils import obj_dict


class NeoWsService(BaseAPI):
    """Service for the Near Earth Object Web Service (NeoWs) API."""

    endpoint_prefix: str = "/neo/rest/v1"

    def feed(self, neo_feed_request: Optional[NeoFeedRequest] = None) -> NeoFeed:
        """
        Retrieve asteroids based on their closest approach date to Earth.

        Args:
            neo_feed_request: Optional date range (defaults to the next 7 days).

        Returns:
            NeoFeed with a collection of near-Earth objects grouped by date.

        Raises:
            NasaAPIException: If the API request fails.
        """
        return self._parse_one(
            f"{self.endpoint_prefix}/feed",
            NeoFeed,
            params=obj_dict(neo_feed_request) if neo_feed_request else None,
        )

    def lookup(self, asteroid_id: Union[str, int]) -> NearEarthObjectItem:
        """
        Retrieve a single asteroid by its NASA JPL ID.

        Args:
            asteroid_id: The asteroid's NASA JPL small body ID.

        Returns:
            NearEarthObjectItem with full details for the requested asteroid.

        Raises:
            NasaAPIException: If the asteroid is not found or the request fails.
        """
        return self._parse_one(f"{self.endpoint_prefix}/neo/{asteroid_id}", NearEarthObjectItem)

    def browse(self, pagination: Optional[Pagination] = None) -> NeoBrowse:
        """
        Browse the overall asteroid dataset.

        Args:
            pagination: Optional page and size parameters.

        Returns:
            NeoBrowse with a paginated list of near-Earth objects.

        Raises:
            NasaAPIException: If the API request fails.
        """
        return self._parse_one(
            f"{self.endpoint_prefix}/neo/browse",
            NeoBrowse,
            params=obj_dict(pagination) if pagination else None,
        )
