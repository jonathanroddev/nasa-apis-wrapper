import datetime
from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, EPICService


def make_image() -> dict:
    return {
        "identifier": "20260516004555",
        "caption": "This image was taken by NASA's EPIC camera onboard the NOAA DSCOVR spacecraft",
        "image": "epic_1b_20260516004555",
        "version": "04",
        "date": "2026-05-16 00:41:06",
        "centroid_coordinates": {"lat": 18.69873, "lon": 156.357422},
        "dscovr_j2000_position": {"x": 1066371.813061, "y": 930196.616494, "z": 475080.779378},
        "lunar_j2000_position": {"x": 260791.244408, "y": 214873.644429, "z": 125035.367301},
        "sun_j2000_position": {"x": 87136592.800058, "y": 113418991.236113, "z": 49164889.199983},
        "attitude_quaternions": {"q0": -0.15048, "q1": 0.71457, "q2": -0.58872, "q3": 0.34665},
        # coords is a duplicate of the above — should be silently ignored by the model
        "coords": {
            "centroid_coordinates": {"lat": 18.69873, "lon": 156.357422},
            "dscovr_j2000_position": {"x": 1066371.813061, "y": 930196.616494, "z": 475080.779378},
            "lunar_j2000_position": {"x": 260791.244408, "y": 214873.644429, "z": 125035.367301},
            "sun_j2000_position": {"x": 87136592.800058, "y": 113418991.236113, "z": 49164889.199983},
            "attitude_quaternions": {"q0": -0.15048, "q1": 0.71457, "q2": -0.58872, "q3": 0.34665},
        },
    }


class TestEPICService:

    def test_no_api_key_required(self) -> None:
        service = EPICService()
        assert service.host == "https://epic.gsfc.nasa.gov/api"
        assert "api_key" not in (service.session.params or {})

    @patch.object(BaseAPI, "get_request", return_value=[make_image()])
    def test_images_latest(self, _) -> None:
        result = EPICService().images()
        assert len(result) == 1
        assert result[0].identifier == "20260516004555"
        assert isinstance(result[0].date, datetime.datetime)
        assert result[0].date == datetime.datetime(2026, 5, 16, 0, 41, 6)

    @patch.object(BaseAPI, "get_request", return_value=[make_image()])
    def test_images_by_date(self, _) -> None:
        result = EPICService().images("enhanced", date=datetime.date(2026, 5, 16))
        assert result[0].version == "04"

    @patch.object(BaseAPI, "get_request", return_value=[make_image()])
    def test_coords_field_ignored(self, _) -> None:
        result = EPICService().images()
        assert not hasattr(result[0], "coords")

    @patch.object(BaseAPI, "get_request", return_value=["2026-05-16", "2026-05-15", "2026-05-14"])
    def test_available_dates(self, _) -> None:
        result = EPICService().available_dates()
        assert result == ["2026-05-16", "2026-05-15", "2026-05-14"]

    @patch.object(BaseAPI, "get_request", return_value=[{"date": "2026-05-16"}, {"date": "2026-05-15"}])
    def test_all_dates(self, _) -> None:
        result = EPICService().all_dates()
        assert len(result) == 2
        assert result[0].date == "2026-05-16"

    @patch.object(BaseAPI, "get_request", return_value=[make_image()])
    def test_image_url_png(self, _) -> None:
        image = EPICService().images()[0]
        url = EPICService().image_url(image, "natural", fmt="png")
        assert url == "https://epic.gsfc.nasa.gov/archive/natural/2026/05/16/png/epic_1b_20260516004555.png"

    @patch.object(BaseAPI, "get_request", return_value=[make_image()])
    def test_image_url_thumbs(self, _) -> None:
        image = EPICService().images()[0]
        url = EPICService().image_url(image, "natural", fmt="thumbs")
        assert url == "https://epic.gsfc.nasa.gov/archive/natural/2026/05/16/thumbs/epic_1b_20260516004555.jpg"
