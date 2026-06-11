from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, model_validator


# ---------------------------------------------------------------------------
# Sensor readings
# ---------------------------------------------------------------------------

class SensorStats(BaseModel):
    """Statistical summary of a sensor's readings over one Sol."""
    av: float   # average
    ct: int     # sample count
    mn: float   # minimum
    mx: float   # maximum


# ---------------------------------------------------------------------------
# Wind direction
# ---------------------------------------------------------------------------

class WindPoint(BaseModel):
    """Wind readings for one compass sector (22.5° wide)."""
    compass_degrees: float
    compass_point: str          # e.g. "N", "WNW", "SSE"
    compass_right: float        # unit vector X component
    compass_up: float           # unit vector Y component
    ct: int                     # reading count for this sector


class WindDirectionData(BaseModel):
    """
    Wind direction distribution for one Sol.

    ``most_common`` is the dominant wind sector. ``sectors`` holds all sectors
    that recorded at least one reading, keyed by their compass index (``"0"``–
    ``"15"``), where ``"0"`` is North and indices increment clockwise by 22.5°.
    """

    model_config = ConfigDict(extra="ignore")

    most_common: Optional[WindPoint] = None
    sectors: Dict[str, WindPoint] = {}

    @model_validator(mode="before")
    @classmethod
    def _extract_sectors(cls, data: dict) -> dict:
        return {
            "most_common": data.get("most_common"),
            "sectors": {k: v for k, v in data.items() if k.isdigit()},
        }


# ---------------------------------------------------------------------------
# Sol weather data
# ---------------------------------------------------------------------------

class SolData(BaseModel):
    """
    Meteorological data recorded by InSight for one Martian Sol.

    ``AT``, ``HWS``, ``PRE`` and ``WD`` may be absent if the sensor did not
    collect enough data that Sol (indicated by ``validity_checks``).
    """

    AT: Optional[SensorStats] = None      # atmospheric temperature (°C)
    HWS: Optional[SensorStats] = None     # horizontal wind speed (m/s)
    PRE: Optional[SensorStats] = None     # pressure (Pa)
    WD: Optional[WindDirectionData] = None

    First_UTC: str
    Last_UTC: str
    Month_ordinal: int
    Northern_season: str    # e.g. "early winter"
    Southern_season: str    # e.g. "early summer"
    Season: str             # e.g. "fall"


# ---------------------------------------------------------------------------
# Validity checks
# ---------------------------------------------------------------------------

class SensorValidity(BaseModel):
    """Validity assessment for a single sensor on a given Sol."""
    sol_hours_with_data: List[int]
    valid: bool


class SolValidity(BaseModel):
    """Validity assessment for all sensors on a given Sol."""
    AT: Optional[SensorValidity] = None
    HWS: Optional[SensorValidity] = None
    PRE: Optional[SensorValidity] = None
    WD: Optional[SensorValidity] = None


class ValidityChecks(BaseModel):
    """
    Data quality metadata for all evaluated Sols.

    ``sol_hours_required`` is the minimum number of hours with data needed for
    a Sol to be included in the response (always 18). ``sol_validity`` maps
    each checked Sol number to its per-sensor validity assessment.
    """

    model_config = ConfigDict(extra="ignore")

    sol_hours_required: int
    sols_checked: List[str]
    sol_validity: Dict[str, SolValidity] = {}

    @model_validator(mode="before")
    @classmethod
    def _extract_sol_validity(cls, data: dict) -> dict:
        fixed = {"sol_hours_required", "sols_checked"}
        return {
            "sol_hours_required": data.get("sol_hours_required"),
            "sols_checked": data.get("sols_checked", []),
            "sol_validity": {k: v for k, v in data.items() if k not in fixed},
        }


# ---------------------------------------------------------------------------
# Root response
# ---------------------------------------------------------------------------

class InsightWeatherResponse(BaseModel):
    """
    Full response from the InSight Mars Weather Service.

    The API returns a flat JSON object mixing dynamic Sol-number keys with
    ``sol_keys`` and ``validity_checks``. This model restructures that into:

    - ``sol_keys``: ordered list of Sol numbers included in the response.
    - ``sols``: dict mapping each Sol number to its :class:`SolData`.
    - ``validity_checks``: data quality metadata.

    .. note::
        The InSight mission ended on 21 December 2022. The endpoint still
        responds but always returns the same historical data from October 2020
        (Sols 675–681). No new data will ever be available.
    """

    model_config = ConfigDict(extra="ignore")

    sol_keys: List[str]
    sols: Dict[str, SolData]
    validity_checks: ValidityChecks

    @model_validator(mode="before")
    @classmethod
    def _restructure(cls, data: dict) -> dict:
        sol_keys = data.get("sol_keys", [])
        return {
            "sol_keys": sol_keys,
            "sols": {k: data[k] for k in sol_keys if k in data},
            "validity_checks": data.get("validity_checks"),
        }
