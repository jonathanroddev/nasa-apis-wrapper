from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict


MarsRover = Literal["curiosity", "opportunity", "spirit", "perseverance"]


class RoverCamera(BaseModel):
    """Camera metadata embedded in a photo record."""
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str                   # short code, e.g. "FHAZ", "NAVCAM", "MAST"
    rover_id: int
    full_name: str              # e.g. "Front Hazard Avoidance Camera"


class RoverInfo(BaseModel):
    """Lightweight rover record embedded in each photo."""
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    landing_date: str
    launch_date: str
    status: str                 # "active" | "complete"


class MarsRoverPhoto(BaseModel):
    """
    A single photograph from a Mars rover.

    ``sol`` is the Martian solar day on which the photo was taken, counted
    from the rover's landing date. ``img_src`` is the URL of the full-size
    JPEG image hosted on NASA's servers.
    """
    model_config = ConfigDict(extra="ignore")

    id: int
    sol: int
    camera: RoverCamera
    img_src: str
    earth_date: str             # "YYYY-MM-DD"
    rover: RoverInfo


class MarsRoverPhotosResponse(BaseModel):
    """Response from ``GET /mars-photos/api/v1/rovers/{rover}/photos``."""
    photos: List[MarsRoverPhoto]


class MarsRoverLatestPhotosResponse(BaseModel):
    """Response from ``GET /mars-photos/api/v1/rovers/{rover}/latest_photos``."""
    latest_photos: List[MarsRoverPhoto]


# ---------------------------------------------------------------------------
# Rover manifests
# ---------------------------------------------------------------------------

class RoverManifestPhoto(BaseModel):
    """Per-sol entry in a rover's photo manifest."""
    model_config = ConfigDict(extra="ignore")

    sol: int
    earth_date: str
    total_photos: int
    cameras: List[str]          # camera short codes active on that sol


class RoverManifest(BaseModel):
    """
    Full mission manifest for a single rover, returned by
    ``GET /mars-photos/api/v1/rovers/{rover}``.

    ``max_sol`` and ``max_date`` are the most recent sol and Earth date with
    available imagery. ``photos`` lists every sol that has at least one photo.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    landing_date: str
    launch_date: str
    status: str
    max_sol: int
    max_date: str
    total_photos: int
    cameras: List[Dict[str, Any]] = []   # list of {name, full_name}
    photos: List[RoverManifestPhoto] = []


class RoverManifestResponse(BaseModel):
    """Response from ``GET /mars-photos/api/v1/rovers/{rover}``."""
    photo_manifest: RoverManifest


# ---------------------------------------------------------------------------
# Rovers list
# ---------------------------------------------------------------------------

class RoverSummary(BaseModel):
    """Lightweight rover record from ``GET /mars-photos/api/v1/rovers``."""
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    landing_date: str
    launch_date: str
    status: str
    max_sol: int
    max_date: str
    total_photos: int
    cameras: List[Dict[str, Any]] = []


class RoversResponse(BaseModel):
    """Response from ``GET /mars-photos/api/v1/rovers``."""
    rovers: List[RoverSummary]
