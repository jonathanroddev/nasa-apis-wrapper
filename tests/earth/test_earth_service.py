from unittest.mock import MagicMock, patch

import pytest

from nasa_apis_wrapper.base import BaseAPI, NasaAPIException
from nasa_apis_wrapper.earth import EarthAsset, EarthAssetResource, EarthService

FAKE_PNG = b"\x89PNG\r\nfake_image_bytes"

ASSET_RESPONSE = {
    "date": "2014-02-04T03:30:01",
    "url": "https://earthengine.googleapis.com/map/abc123",
    "cloud_score": 0.12,
    "resource": {"dataset": "LANDSAT_8", "planet": "earth"},
    "service_version": "v5000",
}

ASSET_RESPONSE_NO_CLOUD = {
    "date": "2018-06-15T10:22:00",
    "url": "https://earthengine.googleapis.com/map/def456",
    "resource": {"dataset": "LANDSAT_8", "planet": "earth"},
    "service_version": "v5000",
}


@pytest.fixture
def service():
    return EarthService(api_key="TEST_KEY")


def _mock_bytes(content: bytes, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.content = content
    resp.text = "error"
    return resp


class TestEarthServiceInit:
    def test_uses_nasa_host(self, service):
        assert service.host == "https://api.nasa.gov"

    def test_api_key_set(self, service):
        assert service.session.params == {"api_key": "TEST_KEY"}


class TestImagery:
    def test_returns_bytes(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_PNG)):
            result = service.imagery(lat=29.78, lon=-95.33, date="2018-01-01")
        assert result == FAKE_PNG

    def test_passes_lat_lon_dim(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_PNG)) as mock_get:
            service.imagery(lat=48.86, lon=2.35, dim=0.1)
            _, kwargs = mock_get.call_args
            params = kwargs["params"]
            assert params["lat"] == 48.86
            assert params["lon"] == 2.35
            assert params["dim"] == 0.1

    def test_date_optional(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_PNG)) as mock_get:
            service.imagery(lat=0.0, lon=0.0)
            _, kwargs = mock_get.call_args
            assert "date" not in kwargs["params"]

    def test_date_included_when_given(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_PNG)) as mock_get:
            service.imagery(lat=0.0, lon=0.0, date="2021-06-15")
            _, kwargs = mock_get.call_args
            assert kwargs["params"]["date"] == "2021-06-15"

    def test_cloud_score_flag(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_PNG)) as mock_get:
            service.imagery(lat=0.0, lon=0.0, cloud_score=True)
            _, kwargs = mock_get.call_args
            assert kwargs["params"]["cloud_score"] == "True"

    def test_cloud_score_omitted_by_default(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_PNG)) as mock_get:
            service.imagery(lat=0.0, lon=0.0)
            _, kwargs = mock_get.call_args
            assert "cloud_score" not in kwargs["params"]

    def test_hits_correct_endpoint(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_PNG)) as mock_get:
            service.imagery(lat=0.0, lon=0.0)
            url = mock_get.call_args[0][0]
            assert "/planetary/earth/imagery" in url

    def test_raises_on_error(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(b"Not found", 404)):
            with pytest.raises(NasaAPIException):
                service.imagery(lat=0.0, lon=0.0)


class TestAssets:
    def test_returns_earth_asset(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ASSET_RESPONSE):
            result = service.assets(lat=29.78, lon=-95.33, date="2014-02-01")
        assert isinstance(result, EarthAsset)
        assert result.date == "2014-02-04T03:30:01"
        assert result.url == "https://earthengine.googleapis.com/map/abc123"
        assert result.cloud_score == pytest.approx(0.12)

    def test_resource_parsed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ASSET_RESPONSE):
            result = service.assets(lat=29.78, lon=-95.33, date="2014-02-01")
        assert isinstance(result.resource, EarthAssetResource)
        assert result.resource.dataset == "LANDSAT_8"
        assert result.resource.planet == "earth"

    def test_cloud_score_optional(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ASSET_RESPONSE_NO_CLOUD):
            result = service.assets(lat=0.0, lon=0.0, date="2018-06-15")
        assert result.cloud_score is None

    def test_passes_params(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ASSET_RESPONSE) as mock_get:
            service.assets(lat=29.78, lon=-95.33, date="2014-02-01", dim=0.1)
            mock_get.assert_called_once_with(
                "/planetary/earth/assets",
                params={"lat": 29.78, "lon": -95.33, "date": "2014-02-01", "dim": 0.1},
            )
