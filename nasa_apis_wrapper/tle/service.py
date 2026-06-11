from typing import Literal, Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import TLERecord, TLESearchResponse


class TLEService(BaseAPI):
    """
    Service for the NASA TLE (Two-Line Element) API.

    Provides NORAD TLE sets for Earth-orbiting satellites, sourced from
    Space-Track.org and updated continuously. TLEs encode orbital parameters
    in a compact two-line ASCII format used by tracking software (SGP4/SDP4).

    No API key required.

    Two-Line Element format quick reference:

    - Line 1: epoch, drag term (B*), element set number, checksum
    - Line 2: inclination, RAAN, eccentricity, argument of perigee,
      mean anomaly, mean motion (rev/day), revolution number

    Base URL: ``https://tle.ivanstanojevic.me/api``
    """

    def __init__(self):
        super().__init__()
        self.host = "https://tle.ivanstanojevic.me/api"

    def search(
        self,
        query: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        sort: Optional[str] = None,
        sort_dir: Optional[Literal["ASC", "DESC"]] = None,
    ) -> TLESearchResponse:
        """
        Search for satellites by name.

        Args:
            query: Satellite name or fragment (e.g. ``"ISS"``, ``"STARLINK"``).
            page: Page number (1-based, default 1).
            page_size: Results per page (default 20, max 100).
            sort: Field to sort by — ``"satelliteId"``, ``"name"``,
                or ``"date"``.
            sort_dir: Sort direction — ``"ASC"`` (default) or ``"DESC"``.

        Returns:
            TLESearchResponse with ``member`` (list of TLERecord), ``total_items``,
            and ``parameters`` echoing the applied filters.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.search("ISS")
            iss = result.member[0]
            print(iss.name, iss.satellite_id)
            print(iss.line1)
            print(iss.line2)
        """
        params: dict = {"search": query}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        if sort is not None:
            params["sort"] = sort
        if sort_dir is not None:
            params["sort-dir"] = sort_dir
        data = self.get_request("/tle", params=params)
        return TLESearchResponse(**data)

    def get(self, satellite_id: int) -> TLERecord:
        """
        Retrieve the current TLE for a specific satellite.

        Args:
            satellite_id: NORAD catalog number (e.g. ``25544`` for the ISS).

        Returns:
            TLERecord with ``line1``, ``line2``, ``name``, and epoch ``date``.

        Raises:
            NasaAPIException: If the satellite is not found or the request fails.

        Example::

            iss = service.get(25544)
            print(iss.name, iss.date)
            print(iss.line1)
            print(iss.line2)
        """
        data = self.get_request(f"/tle/{satellite_id}")
        return TLERecord(**data)
