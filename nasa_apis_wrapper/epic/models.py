import datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, field_validator


EPICCollection = Literal["natural", "enhanced", "aerosol", "cloud"]
EPICImageFormat = Literal["png", "jpg", "thumbs"]


class Coordinates2D(BaseModel):
    """Geographic coordinates of the Earth's centroid in the image."""
    lat: float
    lon: float


class Position3D(BaseModel):
    """J2000 position vector in kilometres."""
    x: float
    y: float
    z: float


class AttitudeQuaternions(BaseModel):
    """Spacecraft attitude quaternion (q0, q1, q2, q3)."""
    q0: float
    q1: float
    q2: float
    q3: float


class EPICImage(BaseModel):
    """
    Metadata for a single EPIC image.

    The ``date`` field is parsed from the API's ``"YYYY-MM-DD HH:MM:SS"``
    string format into a :class:`datetime.datetime` object.

    The ``coords`` field returned by the API duplicates the top-level position
    fields and is silently ignored (``extra='ignore'``).
    """

    model_config = ConfigDict(extra="ignore")

    identifier: str
    caption: str
    image: str          # filename without extension, e.g. "epic_1b_20260516004555"
    version: str        # zero-padded string, e.g. "04"
    date: datetime.datetime
    centroid_coordinates: Coordinates2D
    dscovr_j2000_position: Position3D
    lunar_j2000_position: Position3D
    sun_j2000_position: Position3D
    attitude_quaternions: AttitudeQuaternions

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str) -> datetime.datetime:
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class EPICDateItem(BaseModel):
    """A date entry returned by ``GET /{collection}/all``."""
    date: str  # "YYYY-MM-DD"


# Type alias for the /available endpoint, which returns a bare list[str]
EPICAvailableDates = List[str]
