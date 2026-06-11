from unittest.mock import patch

from nasa_apis_wrapper import APODService, APODRequest, BaseAPI

SINGLE_APOD = {
    "date": "2022-03-27",
    "explanation": "Long explanation.",
    "hdurl": "A hdurl.",
    "media_type": "image",
    "service_version": "v1",
    "title": "A title.",
    "url": "An url.",
}

VIDEO_APOD = {
    "date": "2022-03-28",
    "explanation": "A video explanation.",
    "media_type": "video",
    "service_version": "v1",
    "thumbnail_url": "https://img.youtube.com/thumb.jpg",
    "title": "A video title.",
    "url": "https://youtube.com/embed/abc123",
}


class TestAPODService:

    @patch.object(BaseAPI, "get_request", return_value=SINGLE_APOD)
    def test_get_apod(self, _) -> None:
        result = APODService("api_key").get_astronomy_picture_of_day()
        assert result.title == "A title."
        assert result.service_version == "v1"
        assert result.thumbnail_url is None

    @patch.object(BaseAPI, "get_request", return_value=VIDEO_APOD)
    def test_get_apod_video_with_thumbnail(self, _) -> None:
        result = APODService("api_key").get_astronomy_picture_of_day()
        assert result.media_type == "video"
        assert result.thumbnail_url == "https://img.youtube.com/thumb.jpg"

    @patch.object(BaseAPI, "get_request", return_value=[SINGLE_APOD, VIDEO_APOD])
    def test_get_astronomy_pictures_date_range(self, _) -> None:
        import datetime
        request = APODRequest(start_date=datetime.date(2022, 3, 27), end_date=datetime.date(2022, 3, 28))
        result = APODService("api_key").get_astronomy_pictures(request)
        assert len(result) == 2
        assert result[0].title == "A title."
        assert result[1].media_type == "video"

    @patch.object(BaseAPI, "get_request", return_value=[SINGLE_APOD, VIDEO_APOD, SINGLE_APOD])
    def test_get_astronomy_pictures_random(self, _) -> None:
        request = APODRequest(count=3)
        result = APODService("api_key").get_astronomy_pictures(request)
        assert len(result) == 3
