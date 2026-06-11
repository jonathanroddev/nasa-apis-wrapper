from unittest.mock import patch

import pytest

from nasa_apis_wrapper.base import BaseAPI
from nasa_apis_wrapper.techtransfer import (
    TechTransferService,
    PatentResult,
    PatentResponse,
    SoftwareResult,
    SoftwareResponse,
    SpinoffResult,
    SpinoffResponse,
    TechTransferItem,
    TechTransferSearchResponse,
)


# Each result is a positional list matching the field order defined in models.py

PATENTS_RESPONSE = {
    "count": 2,
    "total": 42,
    "perpage": 10,
    "page": 0,
    "results": [
        [
            "LAR-18832-1",
            "Advanced Solar Sail System",
            "<p>A compact solar sail design...</p>",
            "Propulsion",
            "Langley Research Center",
            "US 10,123,456",
            "15/123,456",
            "<p>Novel composite boom structure...</p>",
            "https://technology.nasa.gov/t2/img/lar18832.jpg",
            "https://technology.nasa.gov/t2/patents/LAR-18832-1",
        ],
        [
            "GRC-19000-1",
            "Solar-Powered Ion Thruster",
            "<p>Compact ion thruster...</p>",
            "Propulsion",
            "Glenn Research Center",
            None,
            None,
            None,
            None,
            "https://technology.nasa.gov/t2/patents/GRC-19000-1",
        ],
    ],
}

SOFTWARE_RESPONSE = {
    "count": 1,
    "total": 8,
    "perpage": 10,
    "page": 0,
    "results": [
        [
            "ARC-18045-1",
            "Trajectory Optimization Tool",
            "<p>Computes optimal trajectories...</p>",
            "Astrodynamics",
            "Ames Research Center",
            "Open Source",
            "2021-06-15",
            "<p>Uses pseudospectral methods...</p>",
            "https://technology.nasa.gov/t2/img/arc18045.jpg",
            "https://technology.nasa.gov/t2/software/ARC-18045-1",
        ]
    ],
}

SPINOFFS_RESPONSE = {
    "count": 2,
    "total": 15,
    "perpage": 10,
    "page": 0,
    "results": [
        [
            "2019-001",
            "Water Purification System",
            "<p>Derived from ISS water recycling technology...</p>",
            "2019",
            "PureFlow Inc.",
            "Environment and Resources",
            "Johnson Space Center",
            "https://technology.nasa.gov/t2/img/spinoff2019.jpg",
            "https://spinoff.nasa.gov/2019-001",
        ],
        [
            "2022-005",
            "Biomedical Sensor Array",
            "<p>Miniaturized sensor derived from astronaut health monitoring...</p>",
            "2022",
            "MedTech Corp.",
            "Health and Medicine",
            "Johnson Space Center",
            None,
            "https://spinoff.nasa.gov/2022-005",
        ],
    ],
}

SEARCH_RESPONSE = {
    "count": 2,
    "total": 120,
    "perpage": 10,
    "page": 0,
    "results": [
        [
            "LAR-18832-1",
            "Advanced Solar Sail System",
            "<p>A compact solar sail...</p>",
            "patent",
            "Propulsion",
            "Langley Research Center",
            "https://technology.nasa.gov/t2/img/lar18832.jpg",
            "https://technology.nasa.gov/t2/patents/LAR-18832-1",
        ],
        [
            "ARC-18045-1",
            "Trajectory Optimization Tool",
            "<p>Computes optimal trajectories...</p>",
            "software",
            "Astrodynamics",
            "Ames Research Center",
            None,
            "https://technology.nasa.gov/t2/software/ARC-18045-1",
        ],
    ],
}


@pytest.fixture
def service():
    return TechTransferService()


class TestTechTransferServiceInit:
    def test_host(self, service):
        assert service.host == "https://technology.nasa.gov/api"

    def test_accepts_api_key(self):
        svc = TechTransferService(api_key="TEST_KEY")
        assert svc.session.params == {"api_key": "TEST_KEY"}


class TestPatents:
    def test_returns_patent_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PATENTS_RESPONSE):
            result = service.patents("solar")

        assert isinstance(result, PatentResponse)
        assert result.count == 2
        assert result.total == 42
        assert result.perpage == 10
        assert result.page == 0

    def test_patent_results_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PATENTS_RESPONSE):
            result = service.patents("solar")

        assert len(result.results) == 2
        p = result.results[0]
        assert isinstance(p, PatentResult)
        assert p.case_number == "LAR-18832-1"
        assert p.title == "Advanced Solar Sail System"
        assert p.center == "Langley Research Center"
        assert p.patent_number == "US 10,123,456"
        assert p.serial_number == "15/123,456"
        assert p.url == "https://technology.nasa.gov/t2/patents/LAR-18832-1"

    def test_patent_optional_fields_none(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PATENTS_RESPONSE):
            result = service.patents("solar")

        p = result.results[1]
        assert p.patent_number is None
        assert p.serial_number is None
        assert p.abstract is None
        assert p.image_url is None

    def test_patents_passes_query_param(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PATENTS_RESPONSE) as mock_get:
            service.patents("solar sail")
            mock_get.assert_called_once_with("/patent", params={"patent": "solar sail"})


class TestSoftware:
    def test_returns_software_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SOFTWARE_RESPONSE):
            result = service.software("trajectory")

        assert isinstance(result, SoftwareResponse)
        assert result.count == 1
        assert result.total == 8

    def test_software_result_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SOFTWARE_RESPONSE):
            result = service.software("trajectory")

        sw = result.results[0]
        assert isinstance(sw, SoftwareResult)
        assert sw.case_number == "ARC-18045-1"
        assert sw.title == "Trajectory Optimization Tool"
        assert sw.center == "Ames Research Center"
        assert sw.release_type == "Open Source"
        assert sw.release_date == "2021-06-15"

    def test_software_passes_query_param(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SOFTWARE_RESPONSE) as mock_get:
            service.software("propulsion")
            mock_get.assert_called_once_with("/software", params={"software": "propulsion"})


class TestSpinoffs:
    def test_returns_spinoff_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SPINOFFS_RESPONSE):
            result = service.spinoffs("water")

        assert isinstance(result, SpinoffResponse)
        assert result.count == 2
        assert result.total == 15

    def test_spinoff_result_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SPINOFFS_RESPONSE):
            result = service.spinoffs("water")

        sp = result.results[0]
        assert isinstance(sp, SpinoffResult)
        assert sp.id == "2019-001"
        assert sp.title == "Water Purification System"
        assert sp.year == "2019"
        assert sp.company == "PureFlow Inc."
        assert sp.category == "Environment and Resources"
        assert sp.center == "Johnson Space Center"

    def test_spinoff_optional_image_url(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SPINOFFS_RESPONSE):
            result = service.spinoffs("water")

        assert result.results[1].image_url is None

    def test_spinoffs_passes_query_param(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SPINOFFS_RESPONSE) as mock_get:
            service.spinoffs("medical")
            mock_get.assert_called_once_with("/spinoff", params={"spinoff": "medical"})


class TestSearch:
    def test_returns_search_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE):
            result = service.search("rover")

        assert isinstance(result, TechTransferSearchResponse)
        assert result.count == 2
        assert result.total == 120

    def test_search_items_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE):
            result = service.search("rover")

        assert len(result.results) == 2
        item = result.results[0]
        assert isinstance(item, TechTransferItem)
        assert item.id == "LAR-18832-1"
        assert item.title == "Advanced Solar Sail System"
        assert item.type == "patent"
        assert item.category == "Propulsion"
        assert item.center == "Langley Research Center"

    def test_search_mixed_types(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE):
            result = service.search("rover")

        types = [item.type for item in result.results]
        assert "patent" in types
        assert "software" in types

    def test_search_passes_query_param(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE) as mock_get:
            service.search("rover")
            mock_get.assert_called_once_with("/techtransfer", params={"techtransfer": "rover"})


class TestFromListValidator:
    def test_patent_from_list_shorter_than_fields(self):
        short_list = ["LAR-001", "Short Patent"]
        p = PatentResult.model_validate(short_list)
        assert p.case_number == "LAR-001"
        assert p.title == "Short Patent"
        assert p.description is None

    def test_spinoff_from_dict_still_works(self):
        sp = SpinoffResult.model_validate({
            "id": "2023-010",
            "title": "Test Spinoff",
        })
        assert sp.id == "2023-010"
        assert sp.year is None
