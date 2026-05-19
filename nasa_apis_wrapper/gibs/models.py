from typing import List, Literal, Optional

from pydantic import BaseModel


GIBSProjection = Literal["EPSG:4326", "EPSG:3413", "EPSG:3031", "EPSG:3857"]
GIBSTileFormat = Literal["jpg", "png"]
GIBSWMSFormat = Literal["image/jpeg", "image/png"]
GIBSDataType = Literal["best", "std", "nrt", "all"]


class GIBSDomains(BaseModel):
    """
    Temporal availability data for a GIBS layer, returned by DescribeDomains.

    The ``domain`` field is the raw string from the API. It takes two forms:

    - **Comma-separated dates**: ``"2000-02-24,2000-02-26,2000-03-01,..."``
      Use :attr:`dates` to get the list directly.
    - **ISO 8601 interval**: ``"2000-02-24/2024-01-15/P1D"`` (start/end/period).
      Use :attr:`start_date` and :attr:`end_date` to extract bounds.
    """

    layer: str
    domain: str

    @property
    def is_interval(self) -> bool:
        """True when the domain is an ISO 8601 interval (``start/end/period``)."""
        return "/" in self.domain

    @property
    def dates(self) -> Optional[List[str]]:
        """
        List of individual available dates when the domain is comma-separated.
        Returns ``None`` if the domain is an interval — use :attr:`start_date`
        and :attr:`end_date` in that case.
        """
        if self.is_interval:
            return None
        return [d.strip() for d in self.domain.split(",") if d.strip()]

    @property
    def start_date(self) -> Optional[str]:
        """First available date, regardless of domain format."""
        if self.is_interval:
            return self.domain.split("/")[0]
        dates = self.dates
        return dates[0] if dates else None

    @property
    def end_date(self) -> Optional[str]:
        """Last available date, regardless of domain format."""
        if self.is_interval:
            return self.domain.split("/")[1]
        dates = self.dates
        return dates[-1] if dates else None
