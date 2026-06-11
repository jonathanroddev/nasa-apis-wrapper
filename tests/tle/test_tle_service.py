from unittest.mock import patch

import pytest

from nasa_apis_wrapper.base import BaseAPI
from nasa_apis_wrapper.tle import (
    TLEService,
    TLERecord,
    TLESearchParameters,
    TLESearchResponse,
)


LINE1_ISS = "1 25544U 98067A   24015.50000000  .00006000  00000-0  11000-3 0  9993"
LINE2_ISS = "2 25544  51.6400 100.2000 0001234  90.0000 270.0000 15.50000000000000"

LINE1_HST = "1 20580U 90037B   24015.50000000  .00001234  00000-0  56789-4 0  9991"
LINE2_HST = "2 20580  28.4700 200.0000 0002345 180.0000  90.0000 14.90000000000000"

SEARCH_RESPONSE = {
    "@context": "https://tle.ivanstanojevic.me/api/contexts/TleCollection.jsonld",
    "@id": "/api/tle?search=ISS",
    "@type": "hydra:Collection",
    "totalItems": 2,
    "member": [
        {
            "@id": "/api/tle/25544",
            "@type": "TleModel",
            "satelliteId": 25544,
            "name": "ISS (ZARYA)",
            "date": "2024-01-15T12:00:00+00:00",
            "line1": LINE1_ISS,
            "line2": LINE2_ISS,
        },
        {
            "@id": "/api/tle/20580",
            "@type": "TleModel",
            "satelliteId": 20580,
            "name": "HST",
            "date": "2024-01-15T06:00:00+00:00",
            "line1": LINE1_HST,
            "line2": LINE2_HST,
        },
    ],
    "parameters": {
        "search": "ISS",
        "page": 1,
        "page-size": 20,
        "sort": "satelliteId",
        "sort-dir": "ASC",
    },
}

SINGLE_TLE_RESPONSE = {
    "@id": "/api/tle/25544",
    "@type": "TleModel",
    "satelliteId": 25544,
    "name": "ISS (ZARYA)",
    "date": "2024-01-15T12:00:00+00:00",
    "line1": LINE1_ISS,
    "line2": LINE2_ISS,
}


@pytest.fixture
def service():
    return TLEService()


class TestTLEServiceInit:
    def test_host(self, service):
        assert service.host == "https://tle.ivanstanojevic.me/api"

    def test_no_api_key(self, service):
        assert not hasattr(service.session, "params") or service.session.params is None or service.session.params == {}


class TestSearch:
    def test_returns_search_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE):
            result = service.search("ISS")

        assert isinstance(result, TLESearchResponse)
        assert result.total_items == 2

    def test_member_list_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE):
            result = service.search("ISS")

        assert len(result.member) == 2
        iss = result.member[0]
        assert isinstance(iss, TLERecord)
        assert iss.satellite_id == 25544
        assert iss.name == "ISS (ZARYA)"
        assert iss.date == "2024-01-15T12:00:00+00:00"
        assert iss.line1 == LINE1_ISS
        assert iss.line2 == LINE2_ISS

    def test_jsonld_fields_dropped(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE):
            result = service.search("ISS")

        assert not hasattr(result, "@type")
        assert not hasattr(result.member[0], "@id")

    def test_parameters_parsed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE):
            result = service.search("ISS")

        p = result.parameters
        assert isinstance(p, TLESearchParameters)
        assert p.search == "ISS"
        assert p.page == 1
        assert p.page_size == 20
        assert p.sort == "satelliteId"
        assert p.sort_dir == "ASC"

    def test_search_minimal_params(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE) as mock_get:
            service.search("STARLINK")
            mock_get.assert_called_once_with("/tle", params={"search": "STARLINK"})

    def test_search_with_all_params(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE) as mock_get:
            service.search("ISS", page=2, page_size=50, sort="name", sort_dir="DESC")
            mock_get.assert_called_once_with(
                "/tle",
                params={
                    "search": "ISS",
                    "page": 2,
                    "page-size": 50,
                    "sort": "name",
                    "sort-dir": "DESC",
                },
            )

    def test_search_with_page_only(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE) as mock_get:
            service.search("GPS", page=3)
            call_params = mock_get.call_args[1]["params"]
            assert call_params["page"] == 3
            assert "page-size" not in call_params


class TestGet:
    def test_returns_tle_record(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SINGLE_TLE_RESPONSE):
            result = service.get(25544)

        assert isinstance(result, TLERecord)
        assert result.satellite_id == 25544
        assert result.name == "ISS (ZARYA)"
        assert result.line1 == LINE1_ISS
        assert result.line2 == LINE2_ISS

    def test_get_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=SINGLE_TLE_RESPONSE) as mock_get:
            service.get(25544)
            mock_get.assert_called_once_with("/tle/25544")

    def test_get_different_satellite(self, service):
        hst_response = {**SINGLE_TLE_RESPONSE, "satelliteId": 20580, "name": "HST",
                        "line1": LINE1_HST, "line2": LINE2_HST}
        with patch.object(BaseAPI, "get_request", return_value=hst_response) as mock_get:
            result = service.get(20580)
            mock_get.assert_called_once_with("/tle/20580")
        assert result.satellite_id == 20580
        assert result.name == "HST"
