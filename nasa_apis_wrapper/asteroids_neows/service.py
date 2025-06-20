"""
Module for Asteroids - NeoWs service.

This module contains the NeoWsService class, which provides
    methods for retrieving Near Earth Object Web Service data.

Classes:
    NeoWsService: Provides methods for retrieving Near Earth Object Web Service data.
"""

import json
from typing import Optional, Union

from nasa_apis_wrapper.base import BaseAPI
from .models import NeoFeed, NeoFeedRequest, NearEarthObjectItem, NeoBrowse, Pagination
from ..utils import Utils


class NeoWsService(BaseAPI):
    endpoint_prefix: str = "/neo/rest/v1"
    """
    Provides methods for retrieving Near Earth Object Web Service data.

    Attributes:
        endpoint_prefix (str): The prefix for the Near Earth Object Web Service API endpoints.

    Methods:
        feed(neo_feed_request: Optional[NeoFeedRequest] = None):
            Retrieves the feed of near-Earth objects.
        lookup(asteroid_id: Union[str, int]):
            Retrieves information about a specific near-Earth object.

    Notes:
        This class provides a basic implementation for interacting with
            the Near Earth Object Web Service API.
    """

    def feed(self, neo_feed_request: Optional[NeoFeedRequest] = None) -> NeoFeed:
        """
        Retrieves the feed of near-Earth objects.

        Args:
            neo_feed_request (Optional[NeoFeedRequest]): The request object for the feed.
                If not provided, the default request is used.

        Returns:
            NeoFeed: The feed of near-Earth objects.

        Notes:
            This method sends a GET request to the Near Earth Object Web Service API
                to retrieve the feed of near-Earth objects.
            The feed is filtered by the closest approach date to Earth.
        """
        endpoint: str = f"{self.endpoint_prefix}/feed"
        req = self.get_request(
            endpoint,
            params=Utils.obj_dict(neo_feed_request) if neo_feed_request else None,
        )
        response: dict = json.loads(req)
        return NeoFeed(**response)

    def lookup(self, asteroid_id: Union[str, int]) -> NearEarthObjectItem:
        """
        Retrieves information about a specific near-Earth object.

        Args:
            asteroid_id (str or int): The ID of the asteroid to retrieve information for.

        Returns:
            dict: A dictionary containing information about the asteroid.

        Raises:
            ValueError: If the asteroid ID is invalid or not found.

        Notes:
            The asteroid ID can be either a string or an integer. If the ID is not found,
                a ValueError is raised.
        """
        endpoint: str = f"{self.endpoint_prefix}/neo/{asteroid_id}"
        req = self.get_request(endpoint)
        response: dict = json.loads(req)
        return NearEarthObjectItem(**response)

    def browse(self, pagination: Pagination = None) -> NeoBrowse:
        """
        Retrieves the browse results of near-Earth objects.

        Args:
            pagination (Optional[Pagination]): The pagination object.
                If not provided, the default pagination is used.

        Returns:
            NeoBrowse: The browse results of near-Earth objects.

        Notes:
            This method sends a GET request to the
                Near Earth Object Web Service API to retrieve the browse results.
            The results are paginated based on the provided pagination object.
        """
        endpoint: str = f"{self.endpoint_prefix}/neo/browse"
        req = self.get_request(
            endpoint, params=Utils.obj_dict(pagination) if pagination else None
        )
        response: dict = json.loads(req)
        return NeoBrowse(**response)
