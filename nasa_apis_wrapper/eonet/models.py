import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared sub-models (embedded in events)
# ---------------------------------------------------------------------------

class EventCategoryRef(BaseModel):
    """Category reference as embedded in an event."""
    id: str
    title: str


class EventSourceRef(BaseModel):
    """Source reference as embedded in an event. *url* points to the original incident report."""
    id: str
    url: str


class EventGeometry(BaseModel):
    """
    Spatial and temporal data for a single observation of an event.

    *coordinates* follows the GeoJSON spec:
    - ``"Point"`` → ``[longitude, latitude]``
    - ``"Polygon"`` → ``[[[lon, lat], ...]]``
    """
    magnitudeValue: Optional[float] = None
    magnitudeUnit: Optional[str] = None
    date: str  # ISO 8601 datetime, e.g. "2026-05-14T11:04:00Z"
    type: str
    coordinates: Any


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

class EONETEvent(BaseModel):
    """A natural event tracked by EONET."""
    id: str
    title: str
    description: Optional[str] = None
    link: str
    closed: Optional[str] = None  # ISO 8601 datetime; None means the event is still open
    categories: List[EventCategoryRef]
    sources: List[EventSourceRef]
    geometry: List[EventGeometry]


class EONETEventsRequest(BaseModel):
    """Query parameters for ``GET /events`` and ``GET /events/geojson``."""
    source: Optional[str] = None
    category: Optional[str] = None
    status: Optional[Literal["open", "closed", "all"]] = None
    limit: Optional[int] = None
    days: Optional[int] = None
    start: Optional[datetime.date] = None
    end: Optional[datetime.date] = None
    magID: Optional[str] = None
    magMin: Optional[float] = None
    magMax: Optional[float] = None
    bbox: Optional[str] = None


class EONETEventsResponse(BaseModel):
    """Response from ``GET /events``."""
    title: str
    description: str
    link: str
    events: List[EONETEvent]


# ---------------------------------------------------------------------------
# GeoJSON
# ---------------------------------------------------------------------------

class GeoJSONGeometry(BaseModel):
    """GeoJSON geometry object."""
    type: str
    coordinates: Any


class GeoJSONFeatureProperties(BaseModel):
    """Properties block of a GeoJSON feature returned by ``GET /events/geojson``."""
    id: str
    title: str
    description: Optional[str] = None
    link: str
    closed: Optional[str] = None
    date: str
    magnitudeValue: Optional[float] = None
    magnitudeUnit: Optional[str] = None
    categories: List[EventCategoryRef]
    sources: List[EventSourceRef]


class GeoJSONFeature(BaseModel):
    type: str
    properties: GeoJSONFeatureProperties
    geometry: GeoJSONGeometry


class EONETGeoJSONResponse(BaseModel):
    """Response from ``GET /events/geojson`` (GeoJSON FeatureCollection)."""
    type: str
    features: List[GeoJSONFeature]


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

class EONETCategory(BaseModel):
    """An EONET event category (e.g. wildfires, earthquakes)."""
    id: str
    title: str
    link: str
    description: str
    layers: str  # URL to the associated web service layers


class EONETCategoriesResponse(BaseModel):
    """Response from ``GET /categories``."""
    title: str
    description: str
    link: str
    categories: List[EONETCategory]


class EONETCategoryEventsResponse(BaseModel):
    """Response from ``GET /categories/{categoryId}`` — category metadata plus its events."""
    title: str
    description: str
    link: str
    events: List[EONETEvent]


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

class EONETSource(BaseModel):
    """
    A data source that feeds events into EONET.

    *source* is the organisation's homepage; *link* is the EONET query URL for
    events from this source.
    """
    id: str
    title: str
    source: str
    link: str


class EONETSourcesResponse(BaseModel):
    """Response from ``GET /sources``."""
    title: str
    description: str
    link: str
    sources: List[EONETSource]


# ---------------------------------------------------------------------------
# Magnitudes
# ---------------------------------------------------------------------------

class EONETMagnitude(BaseModel):
    """A magnitude type usable as a filter in ``GET /events``."""
    id: str
    name: str
    unit: str
    description: str
    link: str


class EONETMagnitudesResponse(BaseModel):
    """Response from ``GET /magnitudes``."""
    title: str
    description: str
    link: str
    magnitudes: List[EONETMagnitude]


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

class EONETLayer(BaseModel):
    """A web service layer (WMS/WMTS) for satellite imagery visualisation."""
    name: str
    serviceUrl: str
    serviceTypeId: str
    parameters: List[dict]


class EONETLayerCategory(BaseModel):
    """A category with its associated imagery layers."""
    id: str
    title: str
    layers: List[EONETLayer]


class EONETLayersResponse(BaseModel):
    """Response from ``GET /layers`` and ``GET /layers/{categoryId}``."""
    title: str
    description: str
    link: str
    categories: List[EONETLayerCategory]
