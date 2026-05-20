from typing import Any, List, Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    TechportProjectsResponse,
    TechportProjectDetailResponse,
    TechportSearchResponse,
    TechportProgram,
    TechportProgramsResponse,
    TechportOrganization,
    TechportOrganizationsResponse,
    TechportEnumsResponse,
)


class TechportService(BaseAPI):
    """
    Service for the NASA TechPort API.

    TechPort is NASA's database of technology projects, organized by program,
    mission directorate, and NASA Technology Taxonomy (TX). It covers ~20,000
    active and historical projects from SBIR/STTR grants to flagship mission
    technology development efforts. No API key required.

    Technology Readiness Levels (TRL 1–9) track the maturity of each project:

    - TRL 1–3: Basic and applied research
    - TRL 4–6: Technology development and demonstration
    - TRL 7–9: System prototype through flight-proven
    """

    def __init__(self):
        super().__init__()  # TechPort does not require an API key
        self.host = "https://techport.nasa.gov"

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def projects(
        self, updated_since: Optional[str] = None
    ) -> TechportProjectsResponse:
        """
        List all projects (lightweight references).

        Returns a minimal record per project (ID, last-updated date, flags).
        Use :meth:`project` to fetch the full detail for a specific project.

        Args:
            updated_since: Optional date filter in ``"YYYY-MM-DD"`` format.
                If provided, only projects updated on or after this date are
                returned. Without this filter the full catalogue (~20,000
                projects) is returned.

        Returns:
            TechportProjectsResponse with ``projects`` (list of refs) and
            ``totalCount``.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            refs = service.projects(updated_since="2024-01-01")
            for ref in refs.projects[:10]:
                print(ref.projectId, ref.lastUpdated)
        """
        params = {"updatedSince": updated_since} if updated_since else None
        data = self.get_request("/api/projects", params=params)
        return TechportProjectsResponse(**data)

    def project(self, project_id: int) -> TechportProjectDetailResponse:
        """
        Retrieve the full detail record for a single project.

        Args:
            project_id: Numeric project ID (available from :meth:`projects`
                or :meth:`search`).

        Returns:
            TechportProjectDetailResponse with the full ``project`` object
            including contacts, organizations, taxonomy nodes, library items,
            and technology outcomes.

        Raises:
            NasaAPIException: If the project is not found or the request fails.

        Example::

            detail = service.project(182467)
            p = detail.project
            print(p.title, p.status, p.trlCurrent)
            print(p.leadOrganization["organizationName"])
        """
        data = self.get_request(f"/api/projects/{project_id}")
        return TechportProjectDetailResponse(**data)

    def search(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> TechportSearchResponse:
        """
        Search and browse projects with pagination.

        Note: the TechPort public API does not expose text-search or field
        filters via query parameters — the ``results`` list always reflects
        the full catalogue. Use ``limit`` and ``offset`` to page through it.

        Args:
            limit: Maximum number of results to return per page.
            offset: Number of records to skip (0-based). Use with ``limit``
                to paginate.

        Returns:
            TechportSearchResponse with ``results`` (richer project records
            than :meth:`projects`), ``total``, and ``offset``.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            page1 = service.search(limit=50, offset=0)
            print(f"{page1.total} total projects")
            for result in page1.results:
                print(result.projectId, result.title, result.status)
        """
        params: dict = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        data = self.get_request("/api/projects/search", params=params or None)
        return TechportSearchResponse(**data)

    # ------------------------------------------------------------------
    # Programs
    # ------------------------------------------------------------------

    def programs(self, fetch_children: bool = False) -> TechportProgramsResponse:
        """
        List all NASA programs.

        Args:
            fetch_children: If ``True``, includes ``childPrograms`` (nested
                program objects) in each program record. Defaults to ``False``.

        Returns:
            TechportProgramsResponse with the full list of programs.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.programs()
            for prog in result.programs:
                if prog.isActive:
                    print(prog.programId, prog.acronymOrTitle)
        """
        params = {"fetchChildren": "true"} if fetch_children else None
        data = self.get_request("/api/programs", params=params)
        return TechportProgramsResponse(**data)

    def program(self, program_id: int) -> TechportProgram:
        """
        Retrieve the full detail for a single program.

        Args:
            program_id: Numeric program ID.

        Returns:
            TechportProgram with description, hierarchy, and responsible
            mission directorate.

        Raises:
            NasaAPIException: If the program is not found.
        """
        data = self.get_request(f"/api/programs/{program_id}")
        return TechportProgram(**data["program"])

    # ------------------------------------------------------------------
    # Organizations
    # ------------------------------------------------------------------

    def organizations(self) -> TechportOrganizationsResponse:
        """
        List all organizations in the TechPort database.

        Returns ~4,000 organizations including NASA centers, industry
        partners, universities, and international agencies.

        Returns:
            TechportOrganizationsResponse with the full list.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request("/api/organizations")
        return TechportOrganizationsResponse(**data)

    def organization(self, organization_id: int) -> TechportOrganization:
        """
        Retrieve the full detail for a single organization.

        Args:
            organization_id: Numeric organization ID.

        Returns:
            TechportOrganization with location, UEI, CAGE code, MSI data,
            and federal set-aside categories.

        Raises:
            NasaAPIException: If the organization is not found.
        """
        data = self.get_request(f"/api/organizations/{organization_id}")
        return TechportOrganization(**data["organization"])

    # ------------------------------------------------------------------
    # Reference data
    # ------------------------------------------------------------------

    def enums(self) -> TechportEnumsResponse:
        """
        Retrieve all system enumeration values.

        Returns label/value pairs for all controlled vocabularies used across
        TechPort: project status types, destination types, organization types,
        contact roles, library item types, technology outcome paths, etc.

        Returns:
            TechportEnumsResponse with an ``enums`` dict mapping enum name to
            a list of ``TechportEnumValue`` objects.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request("/api/enums")
        return TechportEnumsResponse(**data)

    def countries(self) -> List[Any]:
        """
        Retrieve the list of countries used in TechPort.

        Returns:
            Raw list of country dicts with ``countryId``, ``name``, and
            ``abbreviation``.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request("/api/countries")
        return data.get("countries", data)

    def state_territories(self) -> List[Any]:
        """
        Retrieve the list of U.S. states and territories used in TechPort.

        Returns:
            Raw list of state/territory dicts with ``stateTerritoryId``,
            ``name``, ``abbreviation``, and ``countryId``.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request("/api/stateTerritories")
        return data.get("stateTerritories", data)
