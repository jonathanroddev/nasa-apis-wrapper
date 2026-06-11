import datetime
from typing import Any, List, Optional, Union

from nasa_apis_wrapper.base import BaseAPI


def _unwrap(obj: Any) -> Any:
    """
    Recursively unwrap Java/Jackson JSON-LD typed objects.

    The SSC REST API serialises every complex type as a two-element list:
    ``["fully.qualified.ClassName", value]``. This helper strips the type
    prefix so the result can be fed directly into Pydantic models.
    """
    if (
        isinstance(obj, list)
        and len(obj) == 2
        and isinstance(obj[0], str)
        and "." in obj[0]        # heuristic: dotted class name
    ):
        return _unwrap(obj[1])
    if isinstance(obj, list):
        return [_unwrap(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _unwrap(v) for k, v in obj.items()}
    return obj
from .models import (
    CoordinateSystem,
    Observatory,
    GroundStation,
    SSCLocationsRequest,
    SSCLocationsResponse,
    SSCConjunctionsResponse,
    SSCFilesResponse,
)


class SSCService(BaseAPI):
    """
    Service for the NASA Satellite Situation Center (SSC) Web Services REST API.

    Provides satellite trajectory data, ground-station conjunction analysis,
    and geophysical region classification for hundreds of spacecraft. No API
    key required.

    Coordinate systems supported:

    - ``"Gse"`` — Geocentric Solar Ecliptic (X → Sun, most common for
      heliospheric missions)
    - ``"Gsm"`` — Geocentric Solar Magnetospheric (standard for magnetosphere)
    - ``"Geo"`` — Geographic (rotates with Earth, standard lat/lon)
    - ``"Gm"`` — Geomagnetic (aligned with Earth's magnetic dipole)
    - ``"Sm"`` — Solar Magnetic
    - ``"GeiTod"`` / ``"GeiJ2000"`` — Inertial frames

    All positional data is in **kilometres** (Cartesian) or **degrees**
    (latitude/longitude). Arrays in :class:`SatelliteData` are parallel —
    index ``i`` corresponds to the same timestamp across all fields.
    """

    def __init__(self):
        super().__init__()  # SSC does not require an API key
        self.host = "https://sscweb.gsfc.nasa.gov/WS/sscr/2"

    # ------------------------------------------------------------------
    # Catalogue endpoints
    # ------------------------------------------------------------------

    def observatories(self, id: Optional[str] = None) -> List[Observatory]:
        """
        List available satellites and spacecraft.

        Args:
            id: Optional satellite ID to filter results (e.g. ``"ace"``).
                If omitted, returns all available observatories (~500+).

        Returns:
            List of Observatory objects with ID, name, data cadence, and
            available time range.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            obs = service.observatories()
            iss = next(o for o in obs if o.Id == "iss")
            print(iss.Resolution)   # cadence in seconds
            print(iss.EndTime)      # latest available data
        """
        params = {"id": id} if id else None
        raw = self.get_request("/observatories", params=params)
        # SSC serialises as [TypeString, {data}] at every level — unwrap all
        payload = _unwrap(raw)
        obs_list = payload.get("Observatory", []) if isinstance(payload, dict) else []
        return [Observatory(**obs) for obs in obs_list]

    def ground_stations(self) -> List[GroundStation]:
        """
        List all ground tracking stations.

        Returns:
            List of GroundStation objects with ID, name, and geographic
            coordinates (latitude/longitude in degrees).

        Raises:
            NasaAPIException: If the request fails.
        """
        raw = self.get_request("/groundStations")
        payload = _unwrap(raw)
        gs_list = payload.get("GroundStation", []) if isinstance(payload, dict) else []
        return [GroundStation(**gs) for gs in gs_list]

    # ------------------------------------------------------------------
    # Location endpoints
    # ------------------------------------------------------------------

    def locations_get(
        self,
        satellites: Union[str, List[str]],
        start: datetime.datetime,
        end: datetime.datetime,
        coord_systems: Union[str, List[CoordinateSystem]],
        resolution_factor: int = 1,
    ) -> SSCLocationsResponse:
        """
        Retrieve satellite positions using the simple GET interface.

        This method returns basic positional data (X, Y, Z, Lat, Lon,
        LocalTime, RadialLength). For BFieldModel, region classification,
        or B-trace footpoints, use :meth:`locations`.

        Args:
            satellites: Satellite ID or list of IDs (e.g. ``"ace"`` or
                ``["ace", "iss"]``). IDs are case-sensitive and must match
                the catalogue. Use :meth:`observatories` to browse available IDs.
            start: Start of the time range (UTC).
            end: End of the time range (UTC).
            coord_systems: Coordinate system or list of systems. Each system
                requested adds X, Y, Z, Lat, Lon (and LocalTime where
                applicable) to the response.
            resolution_factor: Return 1 of every N data points. Defaults to
                1 (all points). Use higher values to reduce response size for
                long time ranges.

        Returns:
            SSCLocationsResponse with :attr:`Data` containing one
            :class:`SatelliteData` per requested satellite.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            response = service.locations_get(
                satellites=["ace", "wind"],
                start=datetime(2023, 1, 1),
                end=datetime(2023, 1, 1, 6),
                coord_systems=["Gse", "Gsm"],
            )
            for sat in response.Data:
                print(sat.Id, sat.Time[0], sat.Coordinates[0].X[0])
        """
        sat_str = ",".join(satellites) if isinstance(satellites, list) else satellites
        cs_str = (
            ",".join(c.lower() for c in coord_systems)
            if isinstance(coord_systems, list)
            else coord_systems.lower()
        )
        start_str = start.strftime("%Y%m%dT%H%M%SZ")
        end_str = end.strftime("%Y%m%dT%H%M%SZ")
        params = {"resolutionFactor": resolution_factor} if resolution_factor != 1 else None
        data = self.get_request(
            f"/locations/{sat_str}/{start_str}/{end_str}/{cs_str}/",
            params=params,
        )
        return SSCLocationsResponse(**data)

    def locations(self, request: SSCLocationsRequest) -> SSCLocationsResponse:
        """
        Retrieve satellite positions using the full POST interface.

        Supports all output options available in SSC: BFieldModel,
        region classification (magnetosheath, magnetosphere, plasmasheet…),
        distance from boundaries (bow shock, magnetopause, neutral sheet),
        and magnetic field trace footpoints.

        Args:
            request: Typed request object. For advanced features not covered
                by :class:`SSCLocationsRequest`, use :meth:`locations_raw`.

        Returns:
            SSCLocationsResponse with :attr:`Data` containing per-satellite
            positional data.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.post_request("/locations", request.model_dump(exclude_none=True))
        return SSCLocationsResponse(**data)

    def locations_raw(self, body: dict) -> SSCLocationsResponse:
        """
        Retrieve satellite positions with a hand-crafted request body.

        Use this when you need features not exposed by :class:`SSCLocationsRequest`
        (e.g. BFieldModel, LocationFilterOptions, FormatOptions).

        Args:
            body: Raw request dict matching the SSC DataRequest schema.

        Returns:
            SSCLocationsResponse.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.post_request("/locations", body)
        return SSCLocationsResponse(**data)

    # ------------------------------------------------------------------
    # Conjunction endpoint
    # ------------------------------------------------------------------

    def conjunctions(self, body: dict) -> SSCConjunctionsResponse:
        """
        Find time intervals when spacecraft pass near ground stations or
        each other (conjunctions).

        The conjunction body is complex — build it as a dict following the
        SSC ``QueryRequest`` schema. The minimum required fields are
        ``TimeInterval``, ``Conditions`` (list of ``SatelliteCondition``
        and/or ``GroundStationCondition``), and ``ConditionOperator``.

        Args:
            body: Raw dict matching the SSC QueryRequest schema.

        Returns:
            SSCConjunctionsResponse with a list of conjunction time windows
            and the satellite locations at each conjunction.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            response = service.conjunctions({
                "TimeInterval": {
                    "Start": "2023-01-01T00:00:00Z",
                    "End":   "2023-01-02T00:00:00Z",
                },
                "ConditionOperator": "Any",
                "Conditions": [
                    {
                        "@type": "SatelliteCondition",
                        "Satellites": [{"Id": "iss"}],
                        "MinimumNumber": 1,
                    }
                ],
            })
        """
        data = self.post_request("/conjunctions", body)
        return SSCConjunctionsResponse(**data)

    # ------------------------------------------------------------------
    # Visualisation endpoints
    # ------------------------------------------------------------------

    def graphs(self, body: dict) -> SSCFilesResponse:
        """
        Generate an orbit plot, map projection, or time-series graph.

        The server renders the image and returns a temporary download URL.
        Supported graph types (set via ``GraphOptions["@type"]``):
        ``"OrbitGraphOptions"``, ``"MapProjectionGraphOptions"``,
        ``"TimeSeriesGraphOptions"``.

        Args:
            body: Raw dict matching the SSC GraphRequest schema.

        Returns:
            SSCFilesResponse with a list of :class:`FileInfo` objects.
            Use ``response.Files[0].Name`` to get the download URL.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.post_request("/graphs", body)
        return SSCFilesResponse(**data)

    def kml(self, body: dict) -> SSCFilesResponse:
        """
        Generate a KML file for Google Earth visualisation.

        Args:
            body: Dict with ``TimeInterval``, ``Satellites``, and optional
                ``Trajectory``, ``NorthBFieldTraceFootpoint``,
                ``SouthBFieldTraceFootpoint`` booleans.

        Returns:
            SSCFilesResponse with the KML file download URL.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            response = service.kml({
                "TimeInterval": {
                    "Start": "2023-01-01T00:00:00Z",
                    "End":   "2023-01-01T06:00:00Z",
                },
                "Satellites": [{"Id": "iss", "ResolutionFactor": 1}],
                "Trajectory": True,
            })
            kml_url = response.Files[0].Name
        """
        data = self.post_request("/kml", body)
        return SSCFilesResponse(**data)
