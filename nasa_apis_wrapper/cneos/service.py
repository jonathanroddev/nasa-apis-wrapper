from typing import Any, Dict, List, Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    FireballRequest,
    FireballResponse,
    CADRequest,
    CADResponse,
    SentryRequest,
    SentrySummaryItem,
    ScoutSummaryItem,
    NHATSSummaryItem,
    SBDBQueryRequest,
    JDCalendarResponse,
    SBIdentRequest,
    SBIdentResponse,
    SBRadarRequest,
    SBRadarResponse,
    SBSatellitesRequest,
    SBSatItem,
    SBSatellitesResponse,
    MDesignAccessibleRequest,
    MDesignMapRequest,
    MDesignAccessibleResponse,
    SBObsRequest,
    SBObsResponse,
)


class CNEOSService(BaseAPI):
    """
    Service for the NASA/JPL Solar System Dynamics (SSD) and Center for Near
    Earth Object Studies (CNEOS) APIs.

    Covers 8 of the 13 available endpoints:

    - **Fireball** — atmospheric impact events detected by government sensors
    - **CAD** — asteroid/comet close approaches to planets (past and future)
    - **SBDB** — complete orbital and physical data for a single small body
    - **Sentry** — NEO Earth impact risk assessment (Palermo/Torino scales)
    - **Scout** — orbit/risk estimates for unconfirmed NEOCP candidates
    - **NHATS** — NEOs accessible by human spaceflight missions
    - **SBDB Query** — bulk queries across all small bodies
    - **JD Converter** — Julian date ↔ calendar date conversion

    No API key required. All values in API responses are strings (numbers
    included), even where a float or int would be more natural.
    """

    def __init__(self):
        super().__init__()  # SSD/CNEOS APIs do not require an API key
        self.host = "https://ssd-api.jpl.nasa.gov"

    @staticmethod
    def _to_records(data: list, fields: list) -> List[Dict[str, Any]]:
        """Convert columnar ``[[v1, v2, ...], ...]`` + field names to records."""
        return [dict(zip(fields, row)) for row in data]

    # ------------------------------------------------------------------
    # Fireball
    # ------------------------------------------------------------------

    def fireballs(
        self, request: Optional[FireballRequest] = None
    ) -> FireballResponse:
        """
        Retrieve atmospheric fireball (bolide) impact events.

        Events are detected by U.S. Government sensors and reported by CNEOS.
        Energy thresholds typically mean only events above ~1 ton TNT equivalent
        are captured.

        Args:
            request: Optional filters for date range, energy, altitude, and
                velocity components.

        Returns:
            FireballResponse with ``records`` as a list of dicts. All values are
            strings; location fields (``lat``, ``lon``, ``alt``) may be ``None``
            for events without reliable geographic data.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.fireballs(FireballRequest(
                date_min="2020-01-01",
                limit=10,
                sort="-energy",
            ))
            for event in result.records:
                print(event["date"], event["energy"], event["impact-e"])
        """
        params = request.model_dump(by_alias=True, exclude_none=True) if request else {}
        data = self.get_request("/fireball.api", params=params)
        return FireballResponse(
            count=data["count"],
            fields=data["fields"],
            records=self._to_records(data.get("data", []), data["fields"]),
        )

    # ------------------------------------------------------------------
    # Close Approach Data
    # ------------------------------------------------------------------

    def close_approaches(
        self, request: Optional[CADRequest] = None
    ) -> CADResponse:
        """
        Retrieve close approaches of asteroids and comets to planets.

        By default returns approaches to Earth within 0.05 au for the next
        60 days. Supports historical queries, PHAs-only filtering, and
        approaches to other planets.

        Args:
            request: Optional filters for date range, distance, magnitude,
                velocity, object type, and target body.

        Returns:
            CADResponse with ``records`` as a list of dicts. Key fields:
            ``des`` (designation), ``cd`` (calendar date TDB),
            ``dist`` (au), ``v_rel`` (km/s), ``h`` (magnitude).

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.close_approaches(CADRequest(
                date_min="2024-01-01",
                date_max="2024-12-31",
                dist_max="0.01",
                body="Earth",
            ))
            for ca in result.records:
                print(ca["des"], ca["cd"], ca["dist"], "au")
        """
        params = request.model_dump(by_alias=True, exclude_none=True) if request else {}
        data = self.get_request("/cad.api", params=params)
        return CADResponse(
            count=str(data["count"]),
            total=str(data["total"]) if "total" in data else None,
            fields=data.get("fields", []),
            records=self._to_records(data.get("data", []), data.get("fields", [])),
        )

    # ------------------------------------------------------------------
    # SBDB (Small-Body Database — single object)
    # ------------------------------------------------------------------

    def object(
        self,
        des: Optional[str] = None,
        spk: Optional[int] = None,
        sstr: Optional[str] = None,
        **flags: Any,
    ) -> dict:
        """
        Retrieve complete data for a single small body (asteroid or comet).

        Exactly one of ``des``, ``spk``, or ``sstr`` must be provided.

        Args:
            des: Primary designation (e.g. ``"433"`` for Eros, ``"1P"``
                for Halley's Comet).
            spk: JPL SPK-ID.
            sstr: Search string — designation, name, or wildcard
                (e.g. ``"Eros"``, ``"433*"``).
            **flags: Additional boolean flags supported by the SBDB API,
                e.g. ``phys_par=True``, ``ca_data=True``, ``vi_data=True``,
                ``discovery=True``.

        Returns:
            Raw dict with ``object``, ``orbit``, and optional ``phys_par``,
            ``ca_data``, ``vi_data``, ``discovery`` sections. The structure
            is complex and varies by object — see the SBDB API documentation.

        Raises:
            NasaAPIException: If the object is not found or the request fails.

        Example::

            data = service.object(des="433", phys_par=True)
            print(data["object"]["fullname"])   # "(433) Eros"
            print(data["orbit"]["moid"])         # MOID in au
        """
        params: Dict[str, Any] = {}
        if des:
            params["des"] = des
        if spk:
            params["spk"] = spk
        if sstr:
            params["sstr"] = sstr
        params.update(flags)
        return self.get_request("/sbdb.api", params=params)

    # ------------------------------------------------------------------
    # Sentry
    # ------------------------------------------------------------------

    def sentry_summary(
        self, request: Optional[SentryRequest] = None
    ) -> List[SentrySummaryItem]:
        """
        List all NEOs currently monitored for Earth impact risk.

        Returns one entry per object, sorted by cumulative Palermo Scale
        (descending). Objects remain in Sentry as long as at least one
        virtual impactor exists.

        Args:
            request: Optional filters for H magnitude, Palermo Scale,
                impact probability, and observation recency.

        Returns:
            List of SentrySummaryItem objects ordered by impact risk.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            objects = service.sentry_summary()
            for obj in objects[:5]:
                print(obj.fullname, obj.ps_max, obj.ip, obj.ts_max)
        """
        params = request.model_dump(by_alias=True, exclude_none=True) if request else {}
        data = self.get_request("/sentry.api", params=params)
        return [SentrySummaryItem(**item) for item in data.get("data", [])]

    def sentry_object(
        self,
        des: Optional[str] = None,
        spk: Optional[int] = None,
    ) -> dict:
        """
        Retrieve full impact risk details for a specific Sentry object.

        Args:
            des: Object designation (e.g. ``"99942"`` for Apophis).
            spk: JPL SPK-ID.

        Returns:
            Raw dict with ``summary`` (aggregate statistics) and ``data``
            (one entry per virtual impactor date). May contain an ``error``
            key if the object was removed from Sentry.

        Raises:
            NasaAPIException: If the request fails.
        """
        params: Dict[str, Any] = {}
        if des:
            params["des"] = des
        if spk:
            params["spk"] = spk
        return self.get_request("/sentry.api", params=params)

    # ------------------------------------------------------------------
    # Scout (NEOCP)
    # ------------------------------------------------------------------

    def scout_summary(self) -> List[ScoutSummaryItem]:
        """
        List all unconfirmed NEOCP candidates currently tracked by Scout.

        Scout computes preliminary orbits and NEO/PHA scores for objects
        on the MPC Near-Earth Object Confirmation Page (NEOCP) before they
        are formally designated.

        Returns:
            List of ScoutSummaryItem objects, one per NEOCP candidate.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request("/scout.api")
        return [ScoutSummaryItem(**item) for item in data.get("data", [])]

    def scout_object(self, tdes: str, **params: Any) -> dict:
        """
        Retrieve detailed Scout data for a specific NEOCP candidate.

        Args:
            tdes: Temporary designation of the NEOCP object (e.g.
                ``"P10vY9r"``).
            **params: Optional flags such as ``orbits=True``, ``plot="el:ca"``.

        Returns:
            Raw dict with scores, ephemeris metadata, sampled orbits, and
            optional plot images (Base64 PNG).

        Raises:
            NasaAPIException: If the object is not found or the request fails.
        """
        return self.get_request("/scout.api", params={"tdes": tdes, **params})

    # ------------------------------------------------------------------
    # NHATS (Human-Accessible NEOs)
    # ------------------------------------------------------------------

    def nhats_summary(self, **filters: Any) -> List[NHATSSummaryItem]:
        """
        List NEOs accessible by human spaceflight missions.

        NHATS screens the NEO population for objects reachable within
        given delta-V, mission duration, and stay-time constraints.

        Args:
            **filters: Optional filter parameters:
                ``dv`` (int, 4–12 km/s, default 12),
                ``dur`` (int, 60–450 days, default 450),
                ``stay`` (int, 8–32 days, default 8),
                ``launch`` (str, e.g. ``"2020-2045"``),
                ``h`` (int, max H magnitude),
                ``occ`` (int, max orbital condition code 0–8).

        Returns:
            List of NHATSSummaryItem objects.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            objects = service.nhats_summary(dv=6, dur=360)
            for obj in objects:
                print(obj.fullname, obj.min_dv.dv, "km/s")
        """
        data = self.get_request("/nhats.api", params=filters if filters else None)
        return [NHATSSummaryItem(**item) for item in data.get("data", [])]

    def nhats_object(
        self,
        des: Optional[str] = None,
        spk: Optional[int] = None,
        **filters: Any,
    ) -> dict:
        """
        Retrieve full NHATS trajectory data for a specific NEO.

        Args:
            des: Object designation.
            spk: JPL SPK-ID.
            **filters: Optional filter parameters (same as :meth:`nhats_summary`).

        Returns:
            Raw dict with summary, optimal trajectories (min delta-V and min
            duration), and optional Base64 plot image.

        Raises:
            NasaAPIException: If the request fails.
        """
        params: Dict[str, Any] = {**filters}
        if des:
            params["des"] = des
        if spk:
            params["spk"] = spk
        return self.get_request("/nhats.api", params=params)

    # ------------------------------------------------------------------
    # SBDB Query (bulk)
    # ------------------------------------------------------------------

    def query(
        self,
        fields: str,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        **constraints: Any,
    ) -> List[Dict[str, Any]]:
        """
        Query the Small-Body Database for multiple objects.

        Args:
            fields: Comma-separated list of column names to return.
                Common fields: ``pdes``, ``name``, ``H``, ``diameter``,
                ``e``, ``a``, ``i``, ``neo``, ``pha``, ``class``,
                ``moid``, ``first_obs``, ``last_obs``.
            sort: Field to sort by (prefix ``-`` for descending).
            limit: Maximum number of results to return.
            **constraints: Additional query constraints passed directly as
                query parameters (e.g. ``neo=1``, ``pha=Y``,
                ``class="AMO"``).

        Returns:
            List of dicts, one per object, with the requested fields.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            rows = service.query(
                fields="pdes,name,H,diameter,neo,pha",
                neo=1,
                limit=100,
                sort="-H",
            )
            for row in rows:
                print(row["pdes"], row["H"], row["diameter"])
        """
        params: Dict[str, Any] = {"fields": fields}
        if sort:
            params["sort"] = sort
        if limit:
            params["limit"] = limit
        params.update(constraints)
        data = self.get_request("/sbdb_query.api", params=params)
        return data.get("data", [])

    # ------------------------------------------------------------------
    # JD / Calendar Converter
    # ------------------------------------------------------------------

    def jd_to_date(self, jd: float) -> JDCalendarResponse:
        """
        Convert a Julian Date (JD) to a calendar date.

        Args:
            jd: Julian date value (UT).

        Returns:
            JDCalendarResponse with ``cd`` (formatted date string), ``year``,
            ``month_name``, ``dow_name``, and other calendar fields.

        Raises:
            NasaAPIException: If the JD is out of the supported range.

        Example::

            result = service.jd_to_date(2451545.0)
            print(result.cd)           # "2000-Jan-01 12:00:00"
            print(result.dow_name)     # "Saturday"
        """
        data = self.get_request("/jd_cal.api", params={"jd": jd})
        return JDCalendarResponse(**data)

    def date_to_jd(self, cd: str) -> JDCalendarResponse:
        """
        Convert a calendar date to a Julian Date (JD).

        Args:
            cd: Calendar date string. Supported formats: ``"YYYY-MM-DD"``,
                ``"YYYY-MM-DD hh:mm"``, ``"YYYY-MM-DD hh:mm:ss"``.

        Returns:
            JDCalendarResponse with ``jd`` as the primary result.

        Raises:
            NasaAPIException: If the date format is invalid.

        Example::

            result = service.date_to_jd("2000-01-01 12:00:00")
            print(result.jd)   # "2451545.0000000"
        """
        data = self.get_request("/jd_cal.api", params={"cd": cd})
        return JDCalendarResponse(**data)

    # ------------------------------------------------------------------
    # SB Identification (FOV)
    # ------------------------------------------------------------------

    def identify(self, request: SBIdentRequest) -> SBIdentResponse:
        """
        Identify small bodies present in a specific field of view.

        Useful for planning observations or cross-matching telescope images
        against the known small-body population.

        Args:
            request: Observer location, observation time, and FOV definition.
                Provide the location via ``mpc_code`` or geodetic coordinates
                (``lat`` / ``lon``). Define the FOV via RA/Dec limits or a
                centre + half-width. All other constraints are optional.

        Returns:
            SBIdentResponse with ``records_first`` (first-pass candidates)
            and ``records_second`` (second-pass, only if ``two_pass=True``).
            Each record is a dict with the fields listed in ``fields_first``
            / ``fields_second``.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.identify(SBIdentRequest(
                mpc_code="568",               # Mauna Kea
                obs_time="2024-01-15 06:00",
                fov_ra_center="10 30 00",
                fov_dec_center="+20 00 00",
                vmag_lim=22.0,
            ))
            print(f"{result.n_first_pass} candidates found")
            for obj in result.records_first:
                print(obj["Designation"], obj["Vmag"])
        """
        params = request.model_dump(by_alias=True, exclude_none=True)
        data = self.get_request("/sb_ident.api", params=params)
        fields_first = data.get("fields_first", [])
        fields_second = data.get("fields_second", [])
        return SBIdentResponse(
            n_first_pass=data.get("n_first_pass", 0),
            n_second_pass=data.get("n_second_pass", 0),
            fields_first=fields_first,
            fields_second=fields_second,
            records_first=self._to_records(data.get("data_first_pass", []), fields_first),
            records_second=self._to_records(data.get("data_second_pass", []), fields_second),
            observer=data.get("observer", {}),
        )

    # ------------------------------------------------------------------
    # SB Radar Astrometry
    # ------------------------------------------------------------------

    def radar_astrometry(
        self, request: Optional[SBRadarRequest] = None
    ) -> SBRadarResponse:
        """
        Retrieve radar astrometry (delay and Doppler) measurements.

        Radar astrometry is the most precise orbit-determination technique
        available and is only possible for objects that have passed close
        enough to Earth for Goldstone or Arecibo (before its 2020 collapse)
        to measure.

        Args:
            request: Optional filters for object, measurement type, and
                extra fields (observer, notes, station coordinates).

        Returns:
            SBRadarResponse with ``records`` as a list of dicts. Key fields:
            ``des``, ``epoch`` (UTC), ``value`` (float), ``sigma`` (float),
            ``units`` (``"us"`` for delay, ``"Hz"`` for Doppler),
            ``freq`` (MHz), ``rcvr`` / ``xmit`` (station codes).

        Raises:
            NasaAPIException: If the request fails.
        """
        params = request.model_dump(by_alias=True, exclude_none=True) if request else {}
        data = self.get_request("/sb_radar.api", params=params)
        return SBRadarResponse(
            count=str(data["count"]),
            fields=data["fields"],
            records=self._to_records(data.get("data", []), data["fields"]),
            coords=data.get("coords"),
        )

    # ------------------------------------------------------------------
    # SB Satellites
    # ------------------------------------------------------------------

    def satellites(
        self, request: Optional[SBSatellitesRequest] = None
    ) -> SBSatellitesResponse:
        """
        Retrieve satellite (moon) data for small bodies.

        Several hundred asteroids and comets are known to have natural
        satellites, often discovered via light-curve analysis or direct
        imaging.

        Args:
            request: Optional filters for object, kind, confirmation status,
                and whether to include orbital elements and physical parameters.

        Returns:
            SBSatellitesResponse with ``data`` as a list of SBSatItem objects,
            each containing ``sat`` (identification), ``orbit`` (optional),
            and ``phys_par`` (optional).

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.satellites(SBSatellitesRequest(des="243", orb=True))
            for s in result.data:
                print(s.sat["sat_fullname"], s.orbit.get("per") if s.orbit else "no orbit")
        """
        params = request.model_dump(by_alias=True, exclude_none=True) if request else {}
        data = self.get_request("/sb_sat.api", params=params)
        return SBSatellitesResponse(
            count=str(data["count"]),
            data=[SBSatItem(**item) for item in data.get("data", [])],
        )

    # ------------------------------------------------------------------
    # SB Mission Design
    # ------------------------------------------------------------------

    def mission_design_accessible(
        self, request: Optional[MDesignAccessibleRequest] = None
    ) -> MDesignAccessibleResponse:
        """
        List NEOs accessible by ballistic spacecraft missions (Mode A).

        Screens the NEO population against mission constraints to identify
        the most reachable targets.

        Args:
            request: Optional constraints (record limit, optimality criterion,
                and launch year).

        Returns:
            MDesignAccessibleResponse with ``records`` as a list of dicts.
            Key fields: ``name``, ``date0`` / ``datef`` (launch window),
            ``c3_dep`` (km²/s²), ``vinf_dep`` / ``vinf_arr`` (km/s),
            ``dv_tot`` (km/s), ``tof`` (days), ``H`` (magnitude).

        Raises:
            NasaAPIException: If the request fails.
        """
        params = request.model_dump(by_alias=True, exclude_none=True) if request else {}
        data = self.get_request("/mdesign.api", params=params)
        fields = data.get("fields", [])
        return MDesignAccessibleResponse(
            fields=fields,
            records=self._to_records(data.get("records", []), fields),
            constraints=data.get("constraints", {}),
        )

    def mission_design_query(
        self,
        des: Optional[str] = None,
        spk: Optional[int] = None,
        sstr: Optional[str] = None,
    ) -> dict:
        """
        Retrieve mission design data for a specific NEO (Mode Q).

        Returns launch/arrival windows and trajectory parameters for the
        best missions to the specified object.

        Args:
            des: Object designation (e.g. ``"433"`` for Eros).
            spk: JPL SPK-ID.
            sstr: Search string (name or designation).

        Returns:
            Raw dict with ``object`` metadata, ``fields``, and
            ``selectedMissions`` (list of trajectory parameter arrays).

        Raises:
            NasaAPIException: If the request fails.
        """
        params: Dict[str, Any] = {}
        if des:
            params["des"] = des
        if spk:
            params["spk"] = spk
        if sstr:
            params["sstr"] = sstr
        return self.get_request("/mdesign.api", params=params)

    def mission_design_map(self, request: MDesignMapRequest) -> dict:
        """
        Generate a porkchop-plot dataset for a specific NEO (Mode M).

        Returns a grid of delta-V values over departure date × time-of-flight
        space, suitable for plotting launch opportunity maps.

        Args:
            request: Object identifier plus grid parameters (``mjd0``,
                ``span``, ``tof_min``, ``tof_max``, ``step``).

        Returns:
            Raw dict with ``dep_date``, ``tof``, and 2-D arrays for
            ``vinf_dep``, ``vinf_arr``, ``phase_ang``, ``earth_dist``,
            ``elong_arr``, ``decl_dep``, ``approach_ang``, and
            ``dv_lowthrust``.

        Raises:
            NasaAPIException: If the request fails.
        """
        params = request.model_dump(by_alias=True, exclude_none=True)
        return self.get_request("/mdesign.api", params=params)

    # ------------------------------------------------------------------
    # SB Observability
    # ------------------------------------------------------------------

    def observability(self, request: SBObsRequest) -> SBObsResponse:
        """
        List small bodies observable on a specific night from a given location.

        Applies solar/lunar elevation, elongation, galactic latitude, and
        brightness constraints to filter the entire small-body population
        to only objects actually visible.

        Args:
            request: Observer location (``mpc_code`` or geodetic coordinates),
                observation time, and optional visibility constraints.

        Returns:
            SBObsResponse with ``records`` (one row per observable object),
            ``obs_night`` (twilight, moon rise/set, and dark-time data),
            and object counts.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.observability(SBObsRequest(
                mpc_code="568",             # Mauna Kea
                obs_time="2024-06-15",
                vmag_max=18.0,
                elev_min=30.0,
                output_sort="vmag",
            ))
            print(f"{result.shown_objects} objects visible")
            print("Dark time:", result.obs_night.get("dark_time"))
            for obj in result.records[:5]:
                print(obj["Designation"], obj["Vmag"])
        """
        params = request.model_dump(by_alias=True, exclude_none=True)
        data = self.get_request("/sbwobs.api", params=params)
        fields = data.get("fields", [])
        return SBObsResponse(
            total_objects=data.get("total_objects", 0),
            shown_objects=data.get("shown_objects", 0),
            fields=fields,
            records=self._to_records(data.get("data", []), fields),
            obs_night=data.get("obs_night", {}),
        )
