"""
Module for Asteroids - NeoWs service.

This module contains the NeoWsService class, which provides methods for retrieving Near Earth Object Web Service data.

Classes:
    NeoWsService: Provides methods for retrieving Near Earth Object Web Service data.
"""

import json
from typing import Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import NeoFeed, NeoFeedRequest
from ..utils import Utils


class NeoWsService(BaseAPI):
    # TODO: Add docstring

    def feed(self, neo_feed_request: Optional[NeoFeedRequest] = None) -> NeoFeed:
        # TODO: Add docstring
        endpoint: str = "/neo/rest/v1/feed"
        req = self.get_request(endpoint, params=Utils.obj_dict(neo_feed_request) if neo_feed_request else None)
        response: dict = json.loads(req.text)
        return NeoFeed(**response)
