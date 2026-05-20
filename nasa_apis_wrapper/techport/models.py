from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class TechportCountry(BaseModel):
    countryId: int
    name: str
    abbreviation: str


class TechportStateTerritory(BaseModel):
    model_config = ConfigDict(extra="ignore")

    stateTerritoryId: int
    name: str
    abbreviation: str
    countryId: int
    isTerritory: bool
    country: Optional[TechportCountry] = None


# ---------------------------------------------------------------------------
# Project list (lightweight)
# ---------------------------------------------------------------------------

class TechportProjectRef(BaseModel):
    """Lightweight project reference returned by ``GET /api/projects``."""
    projectId: int
    lastUpdated: str        # "YYYY-M-D" format
    favorited: bool
    detailedFunding: bool


class TechportProjectsResponse(BaseModel):
    """Response from ``GET /api/projects``."""
    projects: List[TechportProjectRef]
    totalCount: int


# ---------------------------------------------------------------------------
# Project detail
# ---------------------------------------------------------------------------

class TechportProject(BaseModel):
    """
    Full project record from ``GET /api/projects/{projectId}``.

    Nested sub-objects (``program``, ``leadOrganization``, ``primaryTx``,
    contacts, library items, etc.) are typed as ``dict`` — their structure is
    deeply nested and varies by project. ``extra="ignore"`` silently drops any
    undocumented fields added by the API in future.

    ``description`` and ``benefits`` fields contain HTML markup.
    """
    model_config = ConfigDict(extra="ignore")

    projectId: int
    title: str
    description: Optional[str] = None      # HTML
    benefits: Optional[str] = None         # HTML
    status: Optional[str] = None           # "Active" | "Planned" | "Completed" | "Canceled"
    releaseStatus: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    startYear: Optional[int] = None
    endYear: Optional[int] = None
    startMonth: Optional[int] = None
    endMonth: Optional[int] = None
    startDateString: Optional[str] = None
    endDateString: Optional[str] = None
    trlBegin: Optional[int] = None         # 1–9 (Technology Readiness Level)
    trlCurrent: Optional[int] = None
    trlEnd: Optional[int] = None
    viewCount: Optional[int] = None
    programId: Optional[int] = None
    lastUpdated: Optional[str] = None
    favorited: bool = False
    detailedFunding: bool = False
    destinationType: List[str] = []        # mission destinations

    # Nested objects — kept as dict due to deep/variable structure
    program: Optional[Dict[str, Any]] = None
    leadOrganization: Optional[Dict[str, Any]] = None
    otherOrganizations: List[Dict[str, Any]] = []
    projectContacts: List[Dict[str, Any]] = []
    programContacts: List[Dict[str, Any]] = []
    primaryTx: Optional[Dict[str, Any]] = None     # primary taxonomy node
    primaryTxTree: List[List[Dict[str, Any]]] = []
    additionalTxs: List[Dict[str, Any]] = []
    additionalTxTree: List[List[Dict[str, Any]]] = []
    libraryItems: List[Dict[str, Any]] = []
    technologyOutcomes: List[Dict[str, Any]] = []
    primaryImage: Optional[Dict[str, Any]] = None
    states: List[Dict[str, Any]] = []


class TechportProjectDetailResponse(BaseModel):
    """Response from ``GET /api/projects/{projectId}``."""
    projectId: int
    project: TechportProject


# ---------------------------------------------------------------------------
# Search results
# ---------------------------------------------------------------------------

class SearchProgram(BaseModel):
    """Program summary as returned by the search endpoint (snake_case fields)."""
    model_config = ConfigDict(extra="ignore")

    title: str
    program_id: int
    acronym: Optional[str] = None
    responsible_md_acronym: Optional[str] = None


class SearchOrganization(BaseModel):
    """Organization summary as returned by the search endpoint (snake_case fields)."""
    model_config = ConfigDict(extra="ignore")

    organization_id: int
    organization_name: str
    organization_type: Optional[str] = None
    organization_role: Optional[str] = None
    city: Optional[str] = None
    state_name: Optional[str] = None
    country_name: Optional[str] = None
    country_abbreviation: Optional[str] = None


class SearchContact(BaseModel):
    """Contact as returned by the search endpoint."""
    model_config = ConfigDict(extra="ignore")

    full_name: str
    email: Optional[str] = None
    orcid: Optional[str] = None
    project_contact_role: Optional[str] = None
    program_contact_role: Optional[str] = None


class TechportSearchResult(BaseModel):
    """
    A single project result from ``GET /api/projects/search``.

    Note: the search endpoint uses snake_case in nested sub-objects, unlike
    the detail endpoint which uses camelCase throughout.
    """
    model_config = ConfigDict(extra="ignore")

    projectId: int
    title: str
    description: Optional[str] = None      # HTML
    benefits: Optional[str] = None         # HTML
    status: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    modifiedDate: Optional[str] = None
    trlBegin: Optional[int] = None
    trlCurrent: Optional[int] = None
    trlEnd: Optional[int] = None
    viewCount: Optional[int] = None
    destinationTypes: List[str] = []
    program: Optional[SearchProgram] = None
    responsibleMd: Optional[Dict[str, Any]] = None
    primaryTx: Optional[Dict[str, Any]] = None
    leadOrganization: Optional[SearchOrganization] = None
    otherOrganizations: List[SearchOrganization] = []
    projectContacts: List[SearchContact] = []
    programContacts: List[SearchContact] = []
    technologyOutcomes: List[Dict[str, Any]] = []
    libraryItems: List[Dict[str, Any]] = []
    states: List[Dict[str, Any]] = []


class TechportSearchResponse(BaseModel):
    """Response from ``GET /api/projects/search``."""
    results: List[TechportSearchResult]
    total: int
    offset: int
    spellingSuggestions: List[str] = []


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------

class TechportProgram(BaseModel):
    """A NASA program record."""
    model_config = ConfigDict(extra="ignore")

    programId: int
    title: str
    acronym: Optional[str] = None
    acronymOrTitle: Optional[str] = None
    isActive: bool
    description: Optional[str] = None      # HTML
    parentProgramId: Optional[int] = None
    responsibleMdOffice: Optional[int] = None
    responsibleMdAcronym: Optional[str] = None
    manageGaps: bool = False
    ableToSelect: bool = False
    childProgramIds: List[int] = []
    responsibleMd: Optional[Dict[str, Any]] = None
    parentProgram: Optional[Dict[str, Any]] = None


class TechportProgramsResponse(BaseModel):
    """Response from ``GET /api/programs``."""
    programs: List[TechportProgram]
    fetchChildren: bool = False


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

class TechportOrganization(BaseModel):
    """A NASA or external organization record."""
    model_config = ConfigDict(extra="ignore")

    organizationId: int
    organizationName: str
    acronym: Optional[str] = None
    organizationType: Optional[str] = None
    organizationTypePretty: Optional[str] = None
    city: Optional[str] = None
    zipCode: Optional[str] = None
    countryId: Optional[int] = None
    stateTerritoryId: Optional[int] = None
    dunsNumber: Optional[str] = None
    uei: Optional[str] = None
    cageCode: Optional[str] = None
    congressionalDistrict: Optional[str] = None
    murepUnitId: Optional[int] = None
    academicDegreeType: Optional[str] = None
    stateTerritory: Optional[TechportStateTerritory] = None
    country: Optional[TechportCountry] = None
    msiData: Dict[str, List[str]] = {}     # {year_str: [category, ...]}
    setAsideData: List[str] = []


class TechportOrganizationsResponse(BaseModel):
    """Response from ``GET /api/organizations``."""
    organizations: List[TechportOrganization]


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TechportEnumValue(BaseModel):
    label: str
    value: str


class TechportEnumsResponse(BaseModel):
    """Response from ``GET /api/enums``. Contains all system enumeration lists."""
    model_config = ConfigDict(extra="ignore")

    enums: Dict[str, List[TechportEnumValue]]
