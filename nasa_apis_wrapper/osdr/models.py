from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# OSDR Data API — Search
# ---------------------------------------------------------------------------

class OSDRSearchRequest(BaseModel):
    """
    Query parameters for ``GET /osdr/data/search``.

    All fields are optional and combinable. Use ``ffield`` + ``fvalue``
    together to filter by a specific metadata field (e.g.
    ``ffield="organism.raw", fvalue="Mus musculus"``).
    """

    model_config = ConfigDict(populate_by_name=True)

    term: Optional[str] = None
    offset: Optional[int] = Field(None, serialization_alias="from")
    size: Optional[int] = None
    type: Optional[str] = None              # "cgene", "nih_geo", "ebi_pride", "mg_rast"
    sort: Optional[str] = None
    order: Optional[Literal["ASC", "DESC"]] = None
    ffield: Optional[str] = None
    fvalue: Optional[str] = None


class OSDRStudyMission(BaseModel):
    """Mission metadata embedded in a study search result."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(alias="Name")
    start_date: str = Field(alias="Start Date")
    end_date: str = Field(alias="End Date")


class OSDRStudyPerson(BaseModel):
    """Principal investigator embedded in a study search result."""

    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(alias="First Name")
    middle_initials: str = Field(alias="Middle Initials")
    last_name: str = Field(alias="Last Name")


class OSDRStudySource(BaseModel):
    """
    Metadata for a single OSDR study from the Elasticsearch ``_source`` field.

    Field names in the raw API use Title Case with spaces — all are mapped
    to Python-friendly snake_case aliases. Use ``extra="ignore"`` to silently
    drop the many additional metadata fields not modelled here.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    accession: Optional[str] = Field(None, alias="Accession")
    study_title: Optional[str] = Field(None, alias="Study Title")
    study_description: Optional[str] = Field(None, alias="Study Description")
    organism: Optional[Any] = None     # str or List[str] depending on study
    project_type: Optional[str] = Field(None, alias="Project Type")
    experiment_platform: Optional[str] = Field(None, alias="Experiment Platform")
    space_program: Optional[str] = Field(None, alias="Space Program")
    managing_nasa_center: Optional[str] = Field(None, alias="Managing NASA Center")
    study_public_release_date: Optional[float] = Field(None, alias="Study Public Release Date")
    thumbnail: Optional[str] = None
    mission: OSDRStudyMission = Field(alias="Mission")
    study_person: OSDRStudyPerson = Field(alias="Study Person")
    flight_program: Optional[str] = Field(None, alias="Flight Program")
    esa_acronym: Optional[str] = Field(None, alias="ESA Acronym")
    data_source_accession: Optional[str] = Field(None, alias="Data Source Accession")
    material_type: Optional[str] = Field(None, alias="Material Type")
    factor_value: Optional[Any] = Field(None, alias="Factor Value")  # str or List[str]
    links: List[str] = []


class OSDRSearchHit(BaseModel):
    """A single study result from the OSDR Elasticsearch search."""

    model_config = ConfigDict(populate_by_name=True)

    index: str = Field(alias="_index")
    id: str = Field(alias="_id")
    score: Optional[float] = Field(None, alias="_score")
    source: OSDRStudySource = Field(alias="_source")
    highlight: Optional[Dict[str, List[str]]] = None


class OSDRSearchHits(BaseModel):
    total: int
    max_score: Optional[float] = None
    hits: List[OSDRSearchHit]


class OSDRSearchResponse(BaseModel):
    """Response from ``GET /osdr/data/search``."""

    took: int
    timed_out: bool
    hits: OSDRSearchHits


# ---------------------------------------------------------------------------
# OSDR Data API — Study Files
# ---------------------------------------------------------------------------

class OSDRStudyFile(BaseModel):
    """Metadata for a single file associated with an OSDR study."""

    category: str
    date_created: float                     # Unix timestamp
    date_updated: Union[float, str]         # Unix timestamp or "" if unknown
    file_name: str
    file_size: int                          # bytes
    organization: str
    remote_url: str                         # relative path; use full_url property
    restricted: bool
    subcategory: str
    subdirectory: str
    visible: bool

    @property
    def full_url(self) -> str:
        """Absolute URL to download this file."""
        return f"https://osdr.nasa.gov{self.remote_url}"


class OSDRStudyFiles(BaseModel):
    file_count: int
    study_files: List[OSDRStudyFile]


class OSDRFilesResponse(BaseModel):
    """Response from ``GET /osdr/data/osd/files/{ids}``."""

    hits: int
    page_number: int
    page_size: int
    page_total: int
    total_hits: int
    studies: Dict[str, OSDRStudyFiles]


# ---------------------------------------------------------------------------
# Geode-PY API — Missions
# ---------------------------------------------------------------------------

class OSDRMission(BaseModel):
    """
    A spaceflight mission record from the OSDR Geode-PY relational database.
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    identifier: str
    esID: str
    aliases: List[str] = []
    startDate: Optional[str] = None
    endDate: Optional[str] = None


# ---------------------------------------------------------------------------
# RadLab API
# ---------------------------------------------------------------------------

class RadLabRequest(BaseModel):
    """
    Query parameters for the RadLab radiation measurement API.

    All fields are optional. Comparison operators are encoded as field name
    suffixes (``_gte`` → ``>=``, ``_lte`` → ``<=``). The serialization
    aliases map to the actual query parameter names expected by the API.
    """

    model_config = ConfigDict(populate_by_name=True)

    celestial_body: Optional[str] = None
    spacecraft: Optional[str] = None
    module: Optional[str] = None
    instrument: Optional[str] = None
    instrument_id: Optional[str] = None

    timestamp_gte: Optional[str] = Field(None, serialization_alias="timestamp>=")
    timestamp_lte: Optional[str] = Field(None, serialization_alias="timestamp<=")
    timestamp: Optional[str] = None

    absorbed_dose_rate_gte: Optional[float] = Field(None, serialization_alias="absorbed_dose_rate>=")
    absorbed_dose_rate_lte: Optional[float] = Field(None, serialization_alias="absorbed_dose_rate<=")
    dose_equivalent_rate_gte: Optional[float] = Field(None, serialization_alias="dose_equivalent_rate>=")
    dose_equivalent_rate_lte: Optional[float] = Field(None, serialization_alias="dose_equivalent_rate<=")

    altitude_gte: Optional[float] = Field(None, serialization_alias="altitude>=")
    altitude_lte: Optional[float] = Field(None, serialization_alias="altitude<=")
    latitude_gte: Optional[float] = Field(None, serialization_alias="latitude>=")
    latitude_lte: Optional[float] = Field(None, serialization_alias="latitude<=")


class RadLabMeasurement(BaseModel):
    """
    A single radiation measurement from the RadLab database.

    The API returns a pandas split-format JSON (columns/index/data). The
    available columns vary by query — only timestamp is guaranteed.
    """

    model_config = ConfigDict(extra="ignore")

    timestamp: str                               # ISO 8601
    instrument_id: Optional[str] = None
    instrument: Optional[str] = None
    instrument_family: Optional[str] = None
    spacecraft: Optional[str] = None
    module: Optional[str] = None
    trajectory: Optional[str] = None
    celestial_body: Optional[str] = None

    absorbed_dose_rate: Optional[float] = None  # μGy/hour
    dose_equivalent_rate: Optional[float] = None  # μSv/hour
    flux: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    B: Optional[float] = None
    L: Optional[float] = None
