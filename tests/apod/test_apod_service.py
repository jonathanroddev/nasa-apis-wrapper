import json
from unittest.mock import patch

from nasa_apis_wrapper import APODService, BaseAPI


class TestAPODService:
    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            {
                "date": "2022-03-27",
                "explanation": "Long explanation.",
                "hdurl": "A hdurl.",
                "media_type": "image",
                "service_version": "v1",
                "title": "A title.",
                "url": "An url.",
            }
        ),
    )
    def test_get_apod(self, get_request) -> None:
        apod_service: APODService = APODService("api_key")
        result = apod_service.get_astronomy_picture_of_day()
        assert result
