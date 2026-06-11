from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict


# Planetary body served by Trek
TrekBody = Literal["mars", "moon", "vesta"]

# MIME types accepted by GetTile / GetMap
TrekTileFormat = Literal["image/png", "image/jpeg"]

# Most common OGC tilematrixset identifiers used by Trek
TREK_CRS_GEOGRAPHIC = "urn:ogc:def:crs:EPSG::4326"       # equirectangular, all bodies
TREK_CRS_MARS_POLAR_N = "urn:ogc:def:crs:EPSG::32661"    # Mars north polar
TREK_CRS_MARS_POLAR_S = "urn:ogc:def:crs:EPSG::32761"    # Mars south polar
TREK_CRS_MOON_POLAR_N = "urn:ogc:def:crs:EPSG::104903"   # Moon north polar
TREK_CRS_MOON_POLAR_S = "urn:ogc:def:crs:EPSG::104904"   # Moon south polar


# ---------------------------------------------------------------------------
# WMTS capabilities
# ---------------------------------------------------------------------------

class TrekLayer(BaseModel):
    """A map layer advertised in a Trek WMTS GetCapabilities document."""

    identifier: str
    title: Optional[str] = None
    abstract: Optional[str] = None
    formats: List[str] = []
    tile_matrix_sets: List[str] = []


class TrekCapabilities(BaseModel):
    """
    Parsed response from a Trek WMTS GetCapabilities request.

    ``body`` is the planetary body (``"mars"``, ``"moon"``, or ``"vesta"``).
    ``layers`` lists all available map layers with their supported formats and
    tilematrix sets.
    """

    body: str
    layers: List[TrekLayer]


# ---------------------------------------------------------------------------
# Product search
# ---------------------------------------------------------------------------

class TrekProduct(BaseModel):
    """
    A data product (layer) returned by the Trek product-search endpoint.

    ``product_label`` is the layer identifier usable in WMTS/WMS requests.
    ``data_type`` indicates the category: imagery, topography, geology, etc.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    product_label: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    resolution: Optional[str] = None
    thumbnail_url: Optional[str] = None
    projections: List[str] = []
    extent: Optional[Dict[str, Any]] = None


class TrekProductSearchResponse(BaseModel):
    """Response from the Trek product-search endpoint."""
    model_config = ConfigDict(extra="ignore")

    data: List[TrekProduct] = []
    total_count: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


# ---------------------------------------------------------------------------
# Nomenclature
# ---------------------------------------------------------------------------

class TrekNomenclatureFeature(BaseModel):
    """
    A named planetary surface feature from the IAU nomenclature database.

    ``feature_type`` is the IAU descriptor term: Crater, Mons, Vallis, Planitia,
    Tholus, Patera, Chasma, etc. ``center_lat`` / ``center_lon`` are in decimal
    degrees. ``diameter`` is in kilometres.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: Optional[str] = None
    feature_type: Optional[str] = None
    target: Optional[str] = None
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    diameter: Optional[float] = None
    approval_status: Optional[str] = None
    approval_date: Optional[str] = None
    origin: Optional[str] = None          # etymology / origin of the name


class TrekNomenclatureResponse(BaseModel):
    """Response from the Trek nomenclature-search endpoint."""
    model_config = ConfigDict(extra="ignore")

    features: List[TrekNomenclatureFeature] = []
    total_count: Optional[int] = None


# ---------------------------------------------------------------------------
# Elevation
# ---------------------------------------------------------------------------

class TrekElevation(BaseModel):
    """
    Elevation value at a single point from the Trek DEM endpoint.

    ``elevation`` is in metres relative to the planetary datum (areoid for Mars,
    selenoid for the Moon, Vesta reference ellipsoid for Vesta).
    """
    model_config = ConfigDict(extra="ignore")

    elevation: Optional[float] = None
    unit: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class TrekElevationProfilePoint(BaseModel):
    """A single point in an elevation profile."""
    model_config = ConfigDict(extra="ignore")

    lat: float
    lon: float
    elevation: Optional[float] = None
    distance: Optional[float] = None      # cumulative distance from start (km)


class TrekElevationProfile(BaseModel):
    """
    Elevation profile along a path, returned by the Trek DEM profile endpoint.

    ``points`` are sampled at regular intervals along the path from
    ``(start_lat, start_lon)`` to ``(end_lat, end_lon)``.
    """
    model_config = ConfigDict(extra="ignore")

    points: List[TrekElevationProfilePoint] = []
    unit: Optional[str] = None
    total_distance: Optional[float] = None  # km
