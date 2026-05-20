from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Fireball
# ---------------------------------------------------------------------------

class FireballRequest(BaseModel):
    """Query parameters for the Fireball Data API."""
    model_config = ConfigDict(populate_by_name=True)

    date_min: Optional[str] = Field(None, serialization_alias="date-min")
    date_max: Optional[str] = Field(None, serialization_alias="date-max")
    energy_min: Optional[float] = Field(None, serialization_alias="energy-min")
    energy_max: Optional[float] = Field(None, serialization_alias="energy-max")
    impact_e_min: Optional[float] = Field(None, serialization_alias="impact-e-min")
    impact_e_max: Optional[float] = Field(None, serialization_alias="impact-e-max")
    alt_min: Optional[float] = Field(None, serialization_alias="alt-min")
    alt_max: Optional[float] = Field(None, serialization_alias="alt-max")
    vel_comp: Optional[bool] = Field(None, serialization_alias="vel-comp")
    req_loc: Optional[bool] = Field(None, serialization_alias="req-loc")
    req_alt: Optional[bool] = Field(None, serialization_alias="req-alt")
    req_vel_comp: Optional[bool] = Field(None, serialization_alias="req-vel-comp")
    sort: Optional[str] = None
    limit: Optional[int] = None


class FireballResponse(BaseModel):
    """
    Response from the Fireball Data API.

    ``records`` is a list of dicts built from the columnar ``data`` /
    ``fields`` structure returned by the API. All values are strings or
    ``None`` (many location/altitude fields are absent for some events).

    Key fields per record: ``date``, ``lat``, ``lat-dir``, ``lon``,
    ``lon-dir``, ``alt`` (km), ``vel`` (km/s), ``energy`` (×10¹⁰ J),
    ``impact-e`` (kt).
    """
    count: int
    fields: List[str]
    records: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Close Approach Data (CAD)
# ---------------------------------------------------------------------------

class CADRequest(BaseModel):
    """Query parameters for the Close Approach Data API."""
    model_config = ConfigDict(populate_by_name=True)

    date_min: Optional[str] = Field(None, serialization_alias="date-min")
    date_max: Optional[str] = Field(None, serialization_alias="date-max")
    dist_min: Optional[str] = Field(None, serialization_alias="dist-min")
    dist_max: Optional[str] = Field(None, serialization_alias="dist-max")
    min_dist_min: Optional[str] = Field(None, serialization_alias="min-dist-min")
    min_dist_max: Optional[str] = Field(None, serialization_alias="min-dist-max")
    h_min: Optional[float] = Field(None, serialization_alias="h-min")
    h_max: Optional[float] = Field(None, serialization_alias="h-max")
    v_inf_min: Optional[float] = Field(None, serialization_alias="v-inf-min")
    v_inf_max: Optional[float] = Field(None, serialization_alias="v-inf-max")
    v_rel_min: Optional[float] = Field(None, serialization_alias="v-rel-min")
    v_rel_max: Optional[float] = Field(None, serialization_alias="v-rel-max")
    pha: Optional[bool] = None
    nea: Optional[bool] = None
    comet: Optional[bool] = None
    neo: Optional[bool] = None
    body: Optional[str] = None      # planet name or "ALL"
    sort: Optional[str] = None
    limit: Optional[int] = None
    diameter: Optional[bool] = None
    fullname: Optional[bool] = None
    des: Optional[str] = None
    spk: Optional[int] = None


class CADResponse(BaseModel):
    """
    Response from the Close Approach Data API.

    ``records`` is a list of dicts built from the columnar ``data`` /
    ``fields`` structure. Key fields: ``des``, ``cd`` (calendar date TDB),
    ``dist`` (au, nominal), ``dist_min`` (au, 3-sigma), ``v_rel`` (km/s),
    ``v_inf`` (km/s), ``h`` (magnitude), ``t_sigma_f`` (time uncertainty).
    """
    count: str
    total: Optional[str] = None
    fields: List[str]
    records: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Sentry (NEO Impact Risk)
# ---------------------------------------------------------------------------

class SentryRequest(BaseModel):
    """Query parameters for the Sentry Impact Risk API (summary mode)."""
    model_config = ConfigDict(populate_by_name=True)

    h_max: Optional[float] = Field(None, serialization_alias="h-max")
    ps_min: Optional[int] = Field(None, serialization_alias="ps-min")
    ip_min: Optional[float] = Field(None, serialization_alias="ip-min")
    days: Optional[int] = None


class SentrySummaryItem(BaseModel):
    """One entry in the Sentry impact risk summary table."""
    model_config = ConfigDict(extra="ignore")

    des: str
    fullname: str
    id: str
    h: str                          # absolute magnitude
    ip: str                         # cumulative impact probability
    n_imp: int                      # number of virtual impactors
    ps_cum: str                     # cumulative Palermo Scale
    ps_max: str                     # maximum Palermo Scale
    ts_max: str                     # maximum Torino Scale
    range: str                      # year range (e.g. "2028-2101")
    v_inf: str                      # km/s
    last_obs: str
    last_obs_jd: str
    diameter: Optional[str] = None  # km, if known


# ---------------------------------------------------------------------------
# Scout (NEOCP)
# ---------------------------------------------------------------------------

class ScoutSummaryItem(BaseModel):
    """One entry in the Scout NEOCP candidate summary table."""
    model_config = ConfigDict(extra="ignore")

    objectName: str
    nObs: int
    arc: str
    H: str
    rating: str
    moid: str
    neoScore: str
    phaScore: str
    geocentricScore: str
    ieoScore: str
    lastRun: str
    ra: str
    dec: str
    Vmag: str
    unc: str
    rmsN: Optional[str] = None
    caDist: Optional[str] = None
    vInf: Optional[str] = None


# ---------------------------------------------------------------------------
# NHATS (Human-Accessible NEOs)
# ---------------------------------------------------------------------------

class NHATSTrajSummary(BaseModel):
    """Minimum delta-V or minimum duration trajectory summary."""
    dv: str
    dur: str


class NHATSSummaryItem(BaseModel):
    """One entry in the NHATS human-accessible NEO table."""
    model_config = ConfigDict(extra="ignore")

    des: str
    fullname: str
    orbit_id: str
    h: str
    occ: str
    n_via_traj: int
    min_dv: NHATSTrajSummary
    min_dur: NHATSTrajSummary
    obs_start: str
    obs_end: str
    min_size: str
    max_size: str
    size: Optional[str] = None


# ---------------------------------------------------------------------------
# SBDB Query
# ---------------------------------------------------------------------------

class SBDBQueryRequest(BaseModel):
    """
    Query parameters for the Small-Body Database Query API.

    ``fields`` is a comma-separated list of column names to return.
    Use ``limit`` and ``limit_from`` for pagination.
    """
    model_config = ConfigDict(populate_by_name=True)

    fields: Optional[str] = None
    sort: Optional[str] = None
    limit: Optional[int] = None
    limit_from: Optional[int] = Field(None, serialization_alias="limit-from")
    full_prec: Optional[bool] = Field(None, serialization_alias="full-prec")


# ---------------------------------------------------------------------------
# JD / Calendar Converter
# ---------------------------------------------------------------------------

class JDCalendarResponse(BaseModel):
    """Response from the Julian Date / Calendar Date conversion API."""
    model_config = ConfigDict(extra="ignore")

    jd: str
    cd: Optional[str] = None
    year: Optional[int] = None
    month: Optional[str] = None
    month_name: Optional[str] = None
    doy: Optional[int] = None
    dow: Optional[str] = None
    dow_name: Optional[str] = None
    day_and_time: Optional[str] = None


# ---------------------------------------------------------------------------
# SB Identification (FOV)
# ---------------------------------------------------------------------------

class SBIdentRequest(BaseModel):
    """
    Query parameters for the Small-Body Identification API.

    Provide the observer location via ``mpc_code`` OR geodetic coordinates
    (``lat`` / ``lon`` / ``alt``). Define the field of view either via
    explicit RA/Dec limits (``fov_ra_lim`` / ``fov_dec_lim``) or via a
    centre + half-width (``fov_ra_center`` / ``fov_dec_center`` /
    ``fov_ra_hwidth`` / ``fov_dec_hwidth``).
    """
    model_config = ConfigDict(populate_by_name=True)

    # Observer location
    mpc_code: Optional[str] = Field(None, serialization_alias="mpc-code")
    lat: Optional[float] = None
    lon: Optional[float] = None
    alt: Optional[float] = None

    # Time (required)
    obs_time: str = Field(serialization_alias="obs-time")

    # FOV — limits method
    fov_ra_lim: Optional[str] = Field(None, serialization_alias="fov-ra-lim")
    fov_dec_lim: Optional[str] = Field(None, serialization_alias="fov-dec-lim")

    # FOV — centre + half-width method
    fov_ra_center: Optional[str] = Field(None, serialization_alias="fov-ra-center")
    fov_dec_center: Optional[str] = Field(None, serialization_alias="fov-dec-center")
    fov_ra_hwidth: Optional[float] = Field(None, serialization_alias="fov-ra-hwidth")
    fov_dec_hwidth: Optional[float] = Field(None, serialization_alias="fov-dec-hwidth")

    # Filters
    vmag_lim: Optional[float] = Field(None, serialization_alias="vmag-lim")
    two_pass: Optional[bool] = Field(None, serialization_alias="two-pass")
    mag_required: Optional[bool] = Field(None, serialization_alias="mag-required")
    req_elem: Optional[bool] = Field(None, serialization_alias="req-elem")
    sb_kind: Optional[str] = Field(None, serialization_alias="sb-kind")
    sb_group: Optional[str] = Field(None, serialization_alias="sb-group")


class SBIdentResponse(BaseModel):
    """
    Response from the Small-Body Identification API.

    ``records_first`` contains all candidates that pass the first-pass
    (less strict) filter; ``records_second`` those that pass the more
    rigorous second pass (only present when ``two_pass=True``).
    """
    n_first_pass: int
    n_second_pass: int
    fields_first: List[str]
    fields_second: List[str]
    records_first: List[Dict[str, Any]]
    records_second: List[Dict[str, Any]]
    observer: Dict[str, Any]


# ---------------------------------------------------------------------------
# SB Radar Astrometry
# ---------------------------------------------------------------------------

class SBRadarRequest(BaseModel):
    """Query parameters for the Small-Body Radar Astrometry API."""
    spk: Optional[int] = None
    des: Optional[str] = None
    kind: Optional[str] = None          # "a", "an", "au", "c", "cn", "cu", "n", "u"
    bp: Optional[str] = None            # "P" (peak power) or "C" (centre of mass)
    type: Optional[str] = None          # "R" (delay) or "P" (Doppler)
    observer: Optional[bool] = None
    notes: Optional[bool] = None
    ref: Optional[bool] = None
    fullname: Optional[bool] = None
    modified: Optional[bool] = None
    coords: Optional[bool] = None
    c_coords: Optional[bool] = Field(None, serialization_alias="c-coords")


class SBRadarResponse(BaseModel):
    """
    Response from the Small-Body Radar Astrometry API.

    ``records`` contains one measurement per row. Key fields: ``des``
    (designation), ``epoch`` (UTC datetime string), ``value`` (float),
    ``sigma`` (float), ``units`` (``"us"`` for delay, ``"Hz"`` for Doppler),
    ``freq`` (MHz), ``rcvr`` and ``xmit`` (station codes).

    ``coords`` is populated only when ``coords=True`` was requested.
    """
    count: str
    fields: List[str]
    records: List[Dict[str, Any]]
    coords: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# SB Satellites
# ---------------------------------------------------------------------------

class SBSatellitesRequest(BaseModel):
    """Query parameters for the Small-Body Satellites API."""
    model_config = ConfigDict(populate_by_name=True)

    des: Optional[str] = None
    spk: Optional[int] = None
    kind: Optional[str] = None
    orb: Optional[bool] = None
    sigma: Optional[bool] = None
    phys_par: Optional[bool] = Field(None, serialization_alias="phys-par")
    fullname: Optional[bool] = None
    confirmed: Optional[str] = None    # "all", "Y", "N"


class SBSatItem(BaseModel):
    """Data for one satellite of a small body."""
    model_config = ConfigDict(extra="ignore")

    sat: Dict[str, Any]
    orbit: Optional[Dict[str, Any]] = None
    phys_par: Optional[Dict[str, Any]] = None


class SBSatellitesResponse(BaseModel):
    """Response from the Small-Body Satellites API."""
    count: str
    data: List[SBSatItem]


# ---------------------------------------------------------------------------
# SB Mission Design
# ---------------------------------------------------------------------------

class MDesignAccessibleRequest(BaseModel):
    """Query parameters for SB Mission Design — Mode A (accessible NEOs)."""
    model_config = ConfigDict(populate_by_name=True)

    lim: Optional[int] = None
    crit: Optional[int] = None         # 1–6, optimality criterion
    year: Optional[int] = None


class MDesignMapRequest(BaseModel):
    """Query parameters for SB Mission Design — Mode M (porkchop map)."""
    model_config = ConfigDict(populate_by_name=True)

    des: Optional[str] = None
    spk: Optional[int] = None
    sstr: Optional[str] = None
    mjd0: int = Field(serialization_alias="mjd0")
    span: int = Field(serialization_alias="span")
    tof_min: int = Field(serialization_alias="tof-min")
    tof_max: int = Field(serialization_alias="tof-max")
    step: int = Field(serialization_alias="step")   # 1, 2, 5, 10, 15, 20, or 30


class MDesignAccessibleResponse(BaseModel):
    """Response from SB Mission Design Mode A."""
    fields: List[str]
    records: List[Dict[str, Any]]
    constraints: Dict[str, Any]


# ---------------------------------------------------------------------------
# SB Observability
# ---------------------------------------------------------------------------

class SBObsRequest(BaseModel):
    """
    Query parameters for the Small-Body Observability API.

    Provide the observer location via ``mpc_code`` OR geodetic coordinates.
    ``obs_time`` is required.
    """
    model_config = ConfigDict(populate_by_name=True)

    mpc_code: Optional[str] = Field(None, serialization_alias="mpc-code")
    lat: Optional[float] = None
    lon: Optional[float] = None
    alt: Optional[float] = None

    obs_time: str = Field(serialization_alias="obs-time")
    obs_end: Optional[str] = Field(None, serialization_alias="obs-end")

    elev_min: Optional[float] = Field(None, serialization_alias="elev-min")
    elong_min: Optional[float] = Field(None, serialization_alias="elong-min")
    elong_max: Optional[float] = Field(None, serialization_alias="elong-max")
    glat_min: Optional[float] = Field(None, serialization_alias="glat-min")
    glat_max: Optional[float] = Field(None, serialization_alias="glat-max")
    vmag_min: Optional[float] = Field(None, serialization_alias="vmag-min")
    vmag_max: Optional[float] = Field(None, serialization_alias="vmag-max")
    time_min: Optional[int] = Field(None, serialization_alias="time-min")
    mag_required: Optional[bool] = Field(None, serialization_alias="mag-required")
    maxoutput: Optional[int] = None
    output_sort: Optional[str] = Field(None, serialization_alias="output-sort")
    optical: Optional[bool] = None


class SBObsResponse(BaseModel):
    """
    Response from the Small-Body Observability API.

    ``records`` contains one observable object per row, with fields such as
    designation, rise/transit/set times, RA, Dec, Vmag, elongation, and
    galactic latitude. ``obs_night`` holds solar/lunar ephemeris for the night.
    """
    total_objects: int
    shown_objects: int
    fields: List[str]
    records: List[Dict[str, Any]]
    obs_night: Dict[str, Any]
