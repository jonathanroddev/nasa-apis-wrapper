from unittest.mock import patch

import pytest

from nasa_apis_wrapper.base import BaseAPI
from nasa_apis_wrapper.techport import (
    TechportService,
    TechportProjectRef,
    TechportProjectsResponse,
    TechportProject,
    TechportProjectDetailResponse,
    TechportSearchResult,
    TechportSearchResponse,
    TechportProgram,
    TechportProgramsResponse,
    TechportOrganization,
    TechportOrganizationsResponse,
    TechportEnumValue,
    TechportEnumsResponse,
)


PROJECTS_RESPONSE = {
    "projects": [
        {"projectId": 1001, "lastUpdated": "2024-1-15", "favorited": False, "detailedFunding": True},
        {"projectId": 1002, "lastUpdated": "2024-3-5", "favorited": False, "detailedFunding": False},
    ],
    "totalCount": 2,
}

PROJECT_DETAIL_RESPONSE = {
    "projectId": 182467,
    "project": {
        "projectId": 182467,
        "title": "Advanced Composite Solar Sail System",
        "status": "Active",
        "startYear": 2021,
        "endYear": 2025,
        "trlCurrent": 6,
        "favorited": False,
        "detailedFunding": True,
        "destinationType": ["Low Earth Orbit"],
        "leadOrganization": {"organizationName": "NASA Langley Research Center"},
    },
}

SEARCH_RESPONSE = {
    "results": [
        {
            "projectId": 182467,
            "title": "Advanced Composite Solar Sail System",
            "status": "Active",
            "trlCurrent": 6,
        },
        {
            "projectId": 182468,
            "title": "Lunar Surface Power",
            "status": "Planned",
        },
    ],
    "total": 20000,
    "offset": 0,
    "spellingSuggestions": [],
}

PROGRAMS_RESPONSE = {
    "programs": [
        {
            "programId": 10,
            "title": "Space Technology Mission Directorate",
            "acronym": "STMD",
            "acronymOrTitle": "STMD",
            "isActive": True,
            "manageGaps": False,
            "ableToSelect": True,
            "childProgramIds": [101, 102],
        }
    ],
    "fetchChildren": False,
}

PROGRAM_DETAIL_RESPONSE = {
    "program": {
        "programId": 10,
        "title": "Space Technology Mission Directorate",
        "acronym": "STMD",
        "acronymOrTitle": "STMD",
        "isActive": True,
        "manageGaps": False,
        "ableToSelect": True,
        "childProgramIds": [],
    }
}

ORGANIZATIONS_RESPONSE = {
    "organizations": [
        {
            "organizationId": 4924,
            "organizationName": "NASA Langley Research Center",
            "acronym": "LaRC",
            "organizationType": "NASA_CENTER",
            "city": "Hampton",
            "msiData": {},
            "setAsideData": [],
        },
        {
            "organizationId": 5000,
            "organizationName": "SpaceX",
            "organizationType": "INDUSTRY",
            "msiData": {},
            "setAsideData": ["SB"],
        },
    ]
}

ORGANIZATION_DETAIL_RESPONSE = {
    "organization": {
        "organizationId": 4924,
        "organizationName": "NASA Langley Research Center",
        "acronym": "LaRC",
        "organizationType": "NASA_CENTER",
        "city": "Hampton",
        "msiData": {},
        "setAsideData": [],
    }
}

ENUMS_RESPONSE = {
    "enums": {
        "projectStatus": [
            {"label": "Active", "value": "Active"},
            {"label": "Completed", "value": "Completed"},
            {"label": "Canceled", "value": "Canceled"},
        ],
        "destinationType": [
            {"label": "Low Earth Orbit", "value": "LEO"},
            {"label": "Moon", "value": "Moon"},
        ],
    }
}

COUNTRIES_RESPONSE = {
    "countries": [
        {"countryId": 1, "name": "United States", "abbreviation": "US"},
        {"countryId": 2, "name": "Canada", "abbreviation": "CA"},
    ]
}

STATE_TERRITORIES_RESPONSE = {
    "stateTerritories": [
        {"stateTerritoryId": 1, "name": "Virginia", "abbreviation": "VA", "countryId": 1, "isTerritory": False},
        {"stateTerritoryId": 2, "name": "Texas", "abbreviation": "TX", "countryId": 1, "isTerritory": False},
    ]
}


@pytest.fixture
def service():
    return TechportService()


class TestTechportServiceInit:
    def test_host(self, service):
        assert service.host == "https://techport.nasa.gov"


class TestProjects:
    def test_projects_all(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROJECTS_RESPONSE):
            result = service.projects()

        assert isinstance(result, TechportProjectsResponse)
        assert result.totalCount == 2
        assert len(result.projects) == 2
        assert isinstance(result.projects[0], TechportProjectRef)
        assert result.projects[0].projectId == 1001
        assert result.projects[0].lastUpdated == "2024-1-15"
        assert result.projects[0].detailedFunding is True

    def test_projects_updated_since(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROJECTS_RESPONSE) as mock_get:
            service.projects(updated_since="2024-01-01")
            mock_get.assert_called_once_with(
                "/api/projects", params={"updatedSince": "2024-01-01"}
            )

    def test_projects_no_filter(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROJECTS_RESPONSE) as mock_get:
            service.projects()
            mock_get.assert_called_once_with("/api/projects", params=None)


class TestProjectDetail:
    def test_project_detail(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROJECT_DETAIL_RESPONSE):
            result = service.project(182467)

        assert isinstance(result, TechportProjectDetailResponse)
        assert result.projectId == 182467
        assert isinstance(result.project, TechportProject)
        assert result.project.title == "Advanced Composite Solar Sail System"
        assert result.project.status == "Active"
        assert result.project.trlCurrent == 6
        assert result.project.destinationType == ["Low Earth Orbit"]
        assert result.project.leadOrganization["organizationName"] == "NASA Langley Research Center"

    def test_project_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROJECT_DETAIL_RESPONSE) as mock_get:
            service.project(182467)
            mock_get.assert_called_once_with("/api/projects/182467")


class TestSearch:
    def test_search_defaults(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE) as mock_get:
            result = service.search()
            mock_get.assert_called_once_with("/api/projects/search", params=None)

        assert isinstance(result, TechportSearchResponse)
        assert result.total == 20000
        assert result.offset == 0
        assert len(result.results) == 2
        assert isinstance(result.results[0], TechportSearchResult)
        assert result.results[0].projectId == 182467
        assert result.results[0].title == "Advanced Composite Solar Sail System"

    def test_search_with_pagination(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE) as mock_get:
            service.search(limit=50, offset=100)
            mock_get.assert_called_once_with(
                "/api/projects/search", params={"limit": 50, "offset": 100}
            )

    def test_search_limit_only(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE) as mock_get:
            service.search(limit=10)
            mock_get.assert_called_once_with(
                "/api/projects/search", params={"limit": 10}
            )


class TestPrograms:
    def test_programs(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROGRAMS_RESPONSE):
            result = service.programs()

        assert isinstance(result, TechportProgramsResponse)
        assert len(result.programs) == 1
        prog = result.programs[0]
        assert isinstance(prog, TechportProgram)
        assert prog.programId == 10
        assert prog.acronymOrTitle == "STMD"
        assert prog.isActive is True
        assert prog.childProgramIds == [101, 102]

    def test_programs_fetch_children(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROGRAMS_RESPONSE) as mock_get:
            service.programs(fetch_children=True)
            mock_get.assert_called_once_with("/api/programs", params={"fetchChildren": "true"})

    def test_programs_no_fetch_children(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROGRAMS_RESPONSE) as mock_get:
            service.programs()
            mock_get.assert_called_once_with("/api/programs", params=None)

    def test_program_detail(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROGRAM_DETAIL_RESPONSE):
            result = service.program(10)

        assert isinstance(result, TechportProgram)
        assert result.programId == 10
        assert result.title == "Space Technology Mission Directorate"

    def test_program_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PROGRAM_DETAIL_RESPONSE) as mock_get:
            service.program(10)
            mock_get.assert_called_once_with("/api/programs/10")


class TestOrganizations:
    def test_organizations(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ORGANIZATIONS_RESPONSE):
            result = service.organizations()

        assert isinstance(result, TechportOrganizationsResponse)
        assert len(result.organizations) == 2
        org = result.organizations[0]
        assert isinstance(org, TechportOrganization)
        assert org.organizationId == 4924
        assert org.organizationName == "NASA Langley Research Center"
        assert org.acronym == "LaRC"
        assert org.setAsideData == []

    def test_organizations_set_aside(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ORGANIZATIONS_RESPONSE):
            result = service.organizations()
        assert result.organizations[1].setAsideData == ["SB"]

    def test_organization_detail(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ORGANIZATION_DETAIL_RESPONSE):
            result = service.organization(4924)

        assert isinstance(result, TechportOrganization)
        assert result.organizationId == 4924
        assert result.organizationName == "NASA Langley Research Center"

    def test_organization_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ORGANIZATION_DETAIL_RESPONSE) as mock_get:
            service.organization(4924)
            mock_get.assert_called_once_with("/api/organizations/4924")


class TestEnums:
    def test_enums(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ENUMS_RESPONSE):
            result = service.enums()

        assert isinstance(result, TechportEnumsResponse)
        assert "projectStatus" in result.enums
        assert "destinationType" in result.enums
        statuses = result.enums["projectStatus"]
        assert len(statuses) == 3
        assert isinstance(statuses[0], TechportEnumValue)
        assert statuses[0].label == "Active"
        assert statuses[0].value == "Active"


class TestReferenceData:
    def test_countries(self, service):
        with patch.object(BaseAPI, "get_request", return_value=COUNTRIES_RESPONSE):
            result = service.countries()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "United States"
        assert result[0]["abbreviation"] == "US"

    def test_state_territories(self, service):
        with patch.object(BaseAPI, "get_request", return_value=STATE_TERRITORIES_RESPONSE):
            result = service.state_territories()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Virginia"
        assert result[1]["abbreviation"] == "TX"
