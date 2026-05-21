import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict


CoordinateSystem = Literal["Geo", "Gm", "Gse", "Gsm", "Sm", "GeiTod", "GeiJ2000"]
CoordinateComponent = Literal["X", "Y", "Z", "Lat", "Lon", "Local_Time"]
Hemisphere = Literal["North", "South"]


# ---------------------------------------------------------------------------
# Observatories
# ---------------------------------------------------------------------------

class Observatory(BaseModel):
    """An observable satellite or spacecraft in the SSC catalogue."""
    model_config = ConfigDict(extra="ignore")

    Id: str
    Name: str
    Resolution: Optional[int] = None            # cadence in seconds
    StartTime: Optional[datetime.datetime] = None
    EndTime: Optional[datetime.datetime] = None
    ResourceId: Optional[str] = None            # SPASE URI
    GroupId: List[str] = []




# ---------------------------------------------------------------------------
# Ground Stations
# ---------------------------------------------------------------------------

class GroundLocation(BaseModel):
    Latitude: float
    Longitude: float


class GroundStation(BaseModel):
    """A ground tracking station."""
    Id: str
    Name: str
    Location: GroundLocation




# ---------------------------------------------------------------------------
# Location request models
# ---------------------------------------------------------------------------

class SSCTimeInterval(BaseModel):
    """Time range for a location or conjunction query."""
    Start: str      # ISO 8601, e.g. "2023-01-01T00:00:00Z"
    End: str


class SSCSatellite(BaseModel):
    """A satellite to include in a location request."""
    Id: str
    ResolutionFactor: int = 1           # include 1 of every N points


class SSCCoordinateOption(BaseModel):
    """A coordinate component to return in the location response."""
    CoordinateSystem: CoordinateSystem
    Component: CoordinateComponent


class SSCOutputOptions(BaseModel):
    """Output specification for ``POST /locations``."""
    CoordinateOptions: List[SSCCoordinateOption]
    AllLocationFilters: bool = False


class SSCLocationsRequest(BaseModel):
    """
    Request body for ``POST /locations``.

    For advanced options (BFieldModel, region filters, distance outputs,
    B-trace footpoints) build the request dict manually and use
    :meth:`SSCService.locations_raw`.
    """
    TimeInterval: SSCTimeInterval
    Satellites: List[SSCSatellite]
    OutputOptions: SSCOutputOptions
    Description: Optional[str] = None


# ---------------------------------------------------------------------------
# Location response models
# ---------------------------------------------------------------------------

class CoordinateData(BaseModel):
    """
    Positional data for one satellite in one coordinate system.

    All arrays are parallel to :attr:`SatelliteData.Time`. Components are
    only present if explicitly requested in ``OutputOptions``.
    """
    CoordinateSystem: str
    X: Optional[List[float]] = None         # km
    Y: Optional[List[float]] = None         # km
    Z: Optional[List[float]] = None         # km
    Latitude: Optional[List[float]] = None  # degrees [-90, 90]
    Longitude: Optional[List[float]] = None # degrees
    LocalTime: Optional[List[float]] = None # decimal hours [0, 24]


class BTraceData(BaseModel):
    """Magnetic field trace footpoint data (requires BFieldModel in request)."""
    CoordinateSystem: str
    Hemisphere: str
    Latitude: Optional[List[float]] = None
    Longitude: Optional[List[float]] = None
    ArcLength: Optional[List[float]] = None  # km, length of the field line


class SatelliteData(BaseModel):
    """
    Complete location dataset for one satellite over the requested interval.

    All list fields are parallel — index ``i`` corresponds to ``Time[i]``.
    Fields are only populated if requested via ``OutputOptions``.
    """
    Id: str
    Time: List[datetime.datetime]
    Coordinates: List[CoordinateData] = []

    # Scalar fields (optional — require specific OutputOptions)
    RadialLength: Optional[List[float]] = None              # km from Earth centre
    MagneticStrength: Optional[List[float]] = None          # nT (requires BFieldModel)
    DipoleLValue: Optional[List[float]] = None
    DipoleInvariantLatitude: Optional[List[float]] = None   # degrees

    # Distance fields (require DistanceFromOptions)
    NeutralSheetDistance: Optional[List[float]] = None      # km
    BowShockDistance: Optional[List[float]] = None          # km
    MagnetoPauseDistance: Optional[List[float]] = None      # km
    BGseX: Optional[List[float]] = None                     # nT
    BGseY: Optional[List[float]] = None                     # nT
    BGseZ: Optional[List[float]] = None                     # nT

    # Region and trace fields
    SpacecraftRegion: Optional[List[str]] = None
    BTraceData: Optional[List[BTraceData]] = None


class SSCLocationsResponse(BaseModel):
    """Response from ``GET /locations/{...}`` and ``POST /locations``."""
    StatusCode: str
    StatusSubCode: str
    StatusText: List[str] = []
    Data: List[SatelliteData] = []


# ---------------------------------------------------------------------------
# Conjunctions
# ---------------------------------------------------------------------------

class ConjunctionTimeInterval(BaseModel):
    Start: datetime.datetime
    End: datetime.datetime


class ConjunctionInterval(BaseModel):
    """A time window during which a conjunction condition was satisfied."""
    TimeInterval: ConjunctionTimeInterval
    SatelliteDescription: List[Dict[str, Any]] = []


class SSCConjunctionsResponse(BaseModel):
    """Response from ``POST /conjunctions``."""
    StatusCode: str
    StatusSubCode: str
    StatusText: List[str] = []
    Conjunction: List[ConjunctionInterval] = []


# ---------------------------------------------------------------------------
# Files (graphs and KML)
# ---------------------------------------------------------------------------

class FileInfo(BaseModel):
    """A generated output file hosted temporarily on the SSC server."""
    Name: str                           # download URL
    MimeType: str
    Length: int                         # bytes; -1 if unknown
    LastModified: datetime.datetime


class SSCFilesResponse(BaseModel):
    """Response from ``POST /graphs`` and ``POST /kml``."""
    StatusCode: str
    StatusSubCode: str
    StatusText: List[str] = []
    Files: List[FileInfo] = []
