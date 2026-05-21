from unittest.mock import patch

import pytest

from nasa_apis_wrapper.base import BaseAPI
from nasa_apis_wrapper.mars_rover import (
    MarsRoverService,
    MarsRoverPhoto,
    MarsRoverPhotosResponse,
    MarsRoverLatestPhotosResponse,
    RoverCamera,
    RoverInfo,
    RoverManifest,
    RoverManifestPhoto,
    RoverSummary,
    RoversResponse,
)

# ------------------------------------------------------------------
# Mock data
# ------------------------------------------------------------------

_CAMERA = {"id": 20, "name": "FHAZ", "rover_id": 5, "full_name": "Front Hazard Avoidance Camera"}
_ROVER_INFO = {"id": 5, "name": "Curiosity", "landing_date": "2012-08-06",
               "launch_date": "2011-11-26", "status": "active"}
_PHOTO = {
    "id": 102693,
    "sol": 1000,
    "camera": _CAMERA,
    "img_src": "https://mars.nasa.gov/msl-raw-images/proj/msl/redops/ods/surface/sol/01000/opgs/edr/fcam/FLB_486615455EDR_F0481570FHAZ00323M_.JPG",
    "earth_date": "2015-05-30",
    "rover": _ROVER_INFO,
}
_PHOTO_2 = {**_PHOTO, "id": 102694,
            "camera": {"id": 22, "name": "RHAZ", "rover_id": 5, "full_name": "Rear Hazard Avoidance Camera"}}

PHOTOS_RESPONSE = {"photos": [_PHOTO, _PHOTO_2]}
LATEST_PHOTOS_RESPONSE = {"latest_photos": [_PHOTO]}

ROVERS_RESPONSE = {
    "rovers": [
        {
            "id": 5,
            "name": "Curiosity",
            "landing_date": "2012-08-06",
            "launch_date": "2011-11-26",
            "status": "active",
            "max_sol": 4200,
            "max_date": "2024-01-15",
            "total_photos": 695670,
            "cameras": [
                {"name": "FHAZ", "full_name": "Front Hazard Avoidance Camera"},
                {"name": "NAVCAM", "full_name": "Navigation Camera"},
            ],
        },
        {
            "id": 6,
            "name": "Opportunity",
            "landing_date": "2004-01-25",
            "launch_date": "2003-07-07",
            "status": "complete",
            "max_sol": 5111,
            "max_date": "2018-06-11",
            "total_photos": 198439,
            "cameras": [],
        },
    ]
}

MANIFEST_RESPONSE = {
    "photo_manifest": {
        "name": "Curiosity",
        "landing_date": "2012-08-06",
        "launch_date": "2011-11-26",
        "status": "active",
        "max_sol": 4200,
        "max_date": "2024-01-15",
        "total_photos": 695670,
        "cameras": [{"name": "FHAZ", "full_name": "Front Hazard Avoidance Camera"}],
        "photos": [
            {"sol": 1, "earth_date": "2012-08-07", "total_photos": 16, "cameras": ["FHAZ", "RHAZ", "NAVCAM"]},
            {"sol": 1000, "earth_date": "2015-05-30", "total_photos": 278, "cameras": ["FHAZ", "RHAZ", "MAST", "NAVCAM"]},
        ],
    }
}


@pytest.fixture
def service():
    return MarsRoverService(api_key="TEST_KEY")


# ------------------------------------------------------------------
# Init
# ------------------------------------------------------------------

class TestMarsRoverServiceInit:
    def test_uses_nasa_host(self, service):
        assert service.host == "https://api.nasa.gov"

    def test_api_key_set(self, service):
        assert service.session.params == {"api_key": "TEST_KEY"}


# ------------------------------------------------------------------
# rovers()
# ------------------------------------------------------------------

class TestRovers:
    def test_returns_rovers_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ROVERS_RESPONSE):
            result = service.rovers()
        assert isinstance(result, RoversResponse)
        assert len(result.rovers) == 2

    def test_rover_summary_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ROVERS_RESPONSE):
            result = service.rovers()
        r = result.rovers[0]
        assert isinstance(r, RoverSummary)
        assert r.name == "Curiosity"
        assert r.status == "active"
        assert r.max_sol == 4200
        assert r.total_photos == 695670

    def test_inactive_rover(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ROVERS_RESPONSE):
            result = service.rovers()
        assert result.rovers[1].status == "complete"
        assert result.rovers[1].name == "Opportunity"

    def test_calls_correct_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ROVERS_RESPONSE) as mock_get:
            service.rovers()
            mock_get.assert_called_once_with("/mars-photos/api/v1/rovers")


# ------------------------------------------------------------------
# rover()
# ------------------------------------------------------------------

class TestRover:
    def test_returns_manifest(self, service):
        with patch.object(BaseAPI, "get_request", return_value=MANIFEST_RESPONSE):
            result = service.rover("curiosity")
        assert isinstance(result, RoverManifest)
        assert result.name == "Curiosity"
        assert result.max_sol == 4200
        assert result.total_photos == 695670

    def test_manifest_photos_parsed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=MANIFEST_RESPONSE):
            result = service.rover("curiosity")
        assert len(result.photos) == 2
        sol = result.photos[1]
        assert isinstance(sol, RoverManifestPhoto)
        assert sol.sol == 1000
        assert sol.earth_date == "2015-05-30"
        assert sol.total_photos == 278
        assert "MAST" in sol.cameras

    def test_calls_correct_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=MANIFEST_RESPONSE) as mock_get:
            service.rover("perseverance")
            mock_get.assert_called_once_with("/mars-photos/api/v1/manifests/perseverance")


# ------------------------------------------------------------------
# photos()
# ------------------------------------------------------------------

class TestPhotos:
    def test_returns_photos_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE):
            result = service.photos("curiosity", sol=1000)
        assert isinstance(result, MarsRoverPhotosResponse)
        assert len(result.photos) == 2

    def test_photo_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE):
            result = service.photos("curiosity", sol=1000)
        p = result.photos[0]
        assert isinstance(p, MarsRoverPhoto)
        assert p.id == 102693
        assert p.sol == 1000
        assert p.earth_date == "2015-05-30"
        assert "mars.nasa.gov" in p.img_src

    def test_camera_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE):
            result = service.photos("curiosity", sol=1000)
        cam = result.photos[0].camera
        assert isinstance(cam, RoverCamera)
        assert cam.name == "FHAZ"
        assert cam.full_name == "Front Hazard Avoidance Camera"

    def test_rover_info_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE):
            result = service.photos("curiosity", sol=1000)
        rover = result.photos[0].rover
        assert isinstance(rover, RoverInfo)
        assert rover.name == "Curiosity"
        assert rover.status == "active"

    def test_sol_passed_as_param(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE) as mock_get:
            service.photos("curiosity", sol=1000)
            params = mock_get.call_args[1]["params"]
            assert params["sol"] == 1000
            assert "earth_date" not in params

    def test_earth_date_passed_as_param(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE) as mock_get:
            service.photos("opportunity", earth_date="2015-05-30")
            params = mock_get.call_args[1]["params"]
            assert params["earth_date"] == "2015-05-30"
            assert "sol" not in params

    def test_camera_filter_lowercased(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE) as mock_get:
            service.photos("curiosity", sol=1000, camera="NAVCAM")
            params = mock_get.call_args[1]["params"]
            assert params["camera"] == "navcam"

    def test_page_param(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE) as mock_get:
            service.photos("curiosity", sol=1000, page=2)
            params = mock_get.call_args[1]["params"]
            assert params["page"] == 2

    def test_raises_without_sol_or_date(self, service):
        with pytest.raises(ValueError, match="sol.*earth_date"):
            service.photos("curiosity")

    def test_calls_correct_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PHOTOS_RESPONSE) as mock_get:
            service.photos("spirit", sol=100)
            endpoint = mock_get.call_args[0][0]
            assert "/mars-photos/api/v1/rovers/spirit/photos" in endpoint


# ------------------------------------------------------------------
# latest_photos()
# ------------------------------------------------------------------

class TestLatestPhotos:
    def test_returns_latest_photos_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=LATEST_PHOTOS_RESPONSE):
            result = service.latest_photos("curiosity")
        assert isinstance(result, MarsRoverLatestPhotosResponse)
        assert len(result.latest_photos) == 1

    def test_photo_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=LATEST_PHOTOS_RESPONSE):
            result = service.latest_photos("perseverance")
        assert isinstance(result.latest_photos[0], MarsRoverPhoto)

    def test_no_camera_filter_by_default(self, service):
        with patch.object(BaseAPI, "get_request", return_value=LATEST_PHOTOS_RESPONSE) as mock_get:
            service.latest_photos("curiosity")
            mock_get.assert_called_once_with(
                "/mars-photos/api/v1/rovers/curiosity/latest_photos",
                params=None,
            )

    def test_camera_filter_lowercased(self, service):
        with patch.object(BaseAPI, "get_request", return_value=LATEST_PHOTOS_RESPONSE) as mock_get:
            service.latest_photos("perseverance", camera="MCZ_LEFT")
            params = mock_get.call_args[1]["params"]
            assert params["camera"] == "mcz_left"

    def test_calls_correct_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=LATEST_PHOTOS_RESPONSE) as mock_get:
            service.latest_photos("perseverance")
            endpoint = mock_get.call_args[0][0]
            assert "/mars-photos/api/v1/rovers/perseverance/latest_photos" in endpoint
