from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, model_validator


# ---------------------------------------------------------------------------
# Per-type result models (parsed from columnar list-of-lists)
# ---------------------------------------------------------------------------

class PatentResult(BaseModel):
    """
    A single patent record from ``GET /api/patent``.

    The API returns results as positional arrays; this model maps each index
    to a named field. All fields after ``title`` are Optional because some
    patents omit trailing fields.

    Fields: case_number, title, description (HTML), category, center,
    patent_number, serial_number, abstract (HTML), image_url, url.
    """
    model_config = ConfigDict(extra="ignore")

    case_number: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    center: Optional[str] = None
    patent_number: Optional[str] = None
    serial_number: Optional[str] = None
    abstract: Optional[str] = None
    image_url: Optional[str] = None
    url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _from_list(cls, v: Any) -> Any:
        if isinstance(v, list):
            keys = [
                "case_number", "title", "description", "category",
                "center", "patent_number", "serial_number", "abstract",
                "image_url", "url",
            ]
            return {keys[i]: v[i] for i in range(min(len(keys), len(v)))}
        return v


class SoftwareResult(BaseModel):
    """
    A single software record from ``GET /api/software``.

    Fields: case_number, title, description (HTML), category, center,
    release_type, release_date, abstract (HTML), image_url, url.
    """
    model_config = ConfigDict(extra="ignore")

    case_number: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    center: Optional[str] = None
    release_type: Optional[str] = None
    release_date: Optional[str] = None
    abstract: Optional[str] = None
    image_url: Optional[str] = None
    url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _from_list(cls, v: Any) -> Any:
        if isinstance(v, list):
            keys = [
                "case_number", "title", "description", "category",
                "center", "release_type", "release_date", "abstract",
                "image_url", "url",
            ]
            return {keys[i]: v[i] for i in range(min(len(keys), len(v)))}
        return v


class SpinoffResult(BaseModel):
    """
    A single spinoff record from ``GET /api/spinoff``.

    Spinoffs are commercial products derived from NASA technology.

    Fields: id, title, description (HTML), year, company, category,
    center, image_url, url.
    """
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    description: Optional[str] = None
    year: Optional[str] = None
    company: Optional[str] = None
    category: Optional[str] = None
    center: Optional[str] = None
    image_url: Optional[str] = None
    url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _from_list(cls, v: Any) -> Any:
        if isinstance(v, list):
            keys = [
                "id", "title", "description", "year",
                "company", "category", "center", "image_url", "url",
            ]
            return {keys[i]: v[i] for i in range(min(len(keys), len(v)))}
        return v


class TechTransferItem(BaseModel):
    """
    A single item from the generic ``GET /api/techtransfer`` search.

    This endpoint searches across all technology types; the result arrays
    include a ``type`` field indicating patent, software, or spinoff.

    Fields: id, title, description (HTML), type, category, center,
    image_url, url.
    """
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    description: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    center: Optional[str] = None
    image_url: Optional[str] = None
    url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _from_list(cls, v: Any) -> Any:
        if isinstance(v, list):
            keys = [
                "id", "title", "description", "type",
                "category", "center", "image_url", "url",
            ]
            return {keys[i]: v[i] for i in range(min(len(keys), len(v)))}
        return v


# ---------------------------------------------------------------------------
# Response wrappers
# ---------------------------------------------------------------------------

class PatentResponse(BaseModel):
    """Response from ``GET /api/patent``."""
    count: int
    total: int
    perpage: int
    page: int
    results: List[PatentResult]


class SoftwareResponse(BaseModel):
    """Response from ``GET /api/software``."""
    count: int
    total: int
    perpage: int
    page: int
    results: List[SoftwareResult]


class SpinoffResponse(BaseModel):
    """Response from ``GET /api/spinoff``."""
    count: int
    total: int
    perpage: int
    page: int
    results: List[SpinoffResult]


class TechTransferSearchResponse(BaseModel):
    """Response from ``GET /api/techtransfer`` (cross-type search)."""
    count: int
    total: int
    perpage: int
    page: int
    results: List[TechTransferItem]
