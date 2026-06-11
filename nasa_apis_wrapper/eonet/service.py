from typing import Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    EONETEvent,
    EONETEventsRequest,
    EONETEventsResponse,
    EONETGeoJSONResponse,
    EONETCategoriesResponse,
    EONETCategoryEventsResponse,
    EONETSourcesResponse,
    EONETMagnitudesResponse,
    EONETLayersResponse,
)
from ..utils import obj_dict


class EONETService(BaseAPI):
    """
    Service for the Earth Observatory Natural Event Tracker (EONET) API v3.

    EONET provides near real-time natural event data (wildfires, earthquakes,
    storms, etc.) sourced from multiple scientific agencies. No API key required.
    """

    def __init__(self):
        super().__init__()  # EONET does not require an API key
        self.host = "https://eonet.gsfc.nasa.gov/api/v3"

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def events(self, request: Optional[EONETEventsRequest] = None) -> EONETEventsResponse:
        """
        Retrieve natural events. Returns open events by default.

        Args:
            request: Optional filters (date range, category, status, magnitude, bbox, etc.).

        Returns:
            EONETEventsResponse containing the list of matching events.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self._parse_one("/events", EONETEventsResponse, obj_dict(request) if request else None)

    def event(self, event_id: str) -> EONETEvent:
        """
        Retrieve a single event by its EONET ID.

        Args:
            event_id: EONET event identifier (e.g. ``"EONET_20098"``).

        Returns:
            The full EONETEvent object.

        Raises:
            NasaAPIException: If the event is not found or the request fails.
        """
        return self._parse_one(f"/events/{event_id}", EONETEvent)

    def events_geojson(self, request: Optional[EONETEventsRequest] = None) -> EONETGeoJSONResponse:
        """
        Retrieve natural events as a GeoJSON FeatureCollection.

        Accepts the same filters as :meth:`events`. Each feature's geometry
        represents the most recent observation of the event.

        Args:
            request: Optional filters.

        Returns:
            EONETGeoJSONResponse (GeoJSON FeatureCollection).

        Raises:
            NasaAPIException: If the request fails.
        """
        return self._parse_one("/events/geojson", EONETGeoJSONResponse, obj_dict(request) if request else None)

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def categories(self) -> EONETCategoriesResponse:
        """
        Retrieve all available event categories (e.g. wildfires, earthquakes).

        Returns:
            EONETCategoriesResponse with the full list of categories.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self._parse_one("/categories", EONETCategoriesResponse)

    def category_events(self, category_id: str) -> EONETCategoryEventsResponse:
        """
        Retrieve events filtered by category.

        Args:
            category_id: Category slug (e.g. ``"wildfires"``, ``"earthquakes"``).
                See :meth:`categories` for the full list.

        Returns:
            EONETCategoryEventsResponse with category metadata and matching events.

        Raises:
            NasaAPIException: If the category is not found or the request fails.
        """
        return self._parse_one(f"/categories/{category_id}", EONETCategoryEventsResponse)

    # ------------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------------

    def sources(self) -> EONETSourcesResponse:
        """
        Retrieve all data sources that feed events into EONET.

        Returns:
            EONETSourcesResponse with the full list of contributing organisations.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self._parse_one("/sources", EONETSourcesResponse)

    # ------------------------------------------------------------------
    # Magnitudes
    # ------------------------------------------------------------------

    def magnitudes(self) -> EONETMagnitudesResponse:
        """
        Retrieve all magnitude types available for filtering events.

        Returns:
            EONETMagnitudesResponse with magnitude IDs, units, and descriptions.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self._parse_one("/magnitudes", EONETMagnitudesResponse)

    # ------------------------------------------------------------------
    # Layers
    # ------------------------------------------------------------------

    def layers(self, category_id: Optional[str] = None) -> EONETLayersResponse:
        """
        Retrieve web service layers (WMS/WMTS) for satellite imagery visualisation.

        Args:
            category_id: Optional category slug to retrieve layers for a specific
                category only. If omitted, returns layers for all categories.

        Returns:
            EONETLayersResponse grouped by category.

        Raises:
            NasaAPIException: If the request fails.
        """
        endpoint = f"/layers/{category_id}" if category_id else "/layers"
        return self._parse_one(endpoint, EONETLayersResponse)
