from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TLERecord(BaseModel):
    """
    A Two-Line Element set for a single satellite.

    ``line1`` and ``line2`` are the standard NORAD TLE format strings that
    encode orbital parameters (inclination, eccentricity, RAAN, argument of
    perigee, mean anomaly, mean motion, drag term, epoch, etc.).

    ``date`` is the epoch of the TLE in ISO 8601 format.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    satellite_id: int = Field(alias="satelliteId")
    name: str
    date: str                   # ISO 8601, e.g. "2024-01-15T12:00:00+00:00"
    line1: str                  # NORAD TLE line 1 (69 chars)
    line2: str                  # NORAD TLE line 2 (69 chars)


class TLESearchParameters(BaseModel):
    """Parameters echoed back in a search response."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    search: Optional[str] = None
    page: int = 1
    page_size: int = Field(20, alias="page-size")
    sort: Optional[str] = None
    sort_dir: Optional[str] = Field(None, alias="sort-dir")


class TLESearchResponse(BaseModel):
    """
    Response from ``GET /tle`` (collection search).

    Uses JSON-LD (Hydra) format; ``@context``, ``@id``, and ``@type`` fields
    are silently dropped. ``member`` contains the matching TLE records.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    total_items: int = Field(alias="totalItems")
    member: List[TLERecord]
    parameters: TLESearchParameters
