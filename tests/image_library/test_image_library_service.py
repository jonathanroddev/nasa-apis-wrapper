from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, ImageLibraryService, ImageLibrarySearchRequest

NASA_ID = "as11-40-5931"

SEARCH_RESPONSE = {
    "collection": {
        "version": "1.1",
        "href": "https://images-api.nasa.gov/search?q=Apollo+11&media_type=image",
        "items": [
            {
                "href": f"https://images-assets.nasa.gov/image/{NASA_ID}/collection.json",
                "data": [
                    {
                        "nasa_id": NASA_ID,
                        "title": "Apollo 11 Mission image - Astronaut Edwin Aldrin",
                        "media_type": "image",
                        "date_created": "2018-06-18T00:00:00Z",
                        "center": "HQ",
                        "description": "Astronaut Edwin 'Buzz' Aldrin Jr.",
                        "keywords": ["Apollo 11", "Moon landing"],
                        "photographer": "Neil Armstrong",
                    }
                ],
                "links": [
                    {
                        "href": f"https://images-assets.nasa.gov/image/{NASA_ID}/{NASA_ID}~thumb.jpg",
                        "rel": "preview",
                        "render": "image",
                    },
                    {
                        "href": f"https://images-assets.nasa.gov/image/{NASA_ID}/{NASA_ID}~large.jpg",
                        "rel": "alternate",
                        "render": "image",
                        "width": 1920,
                        "height": 1194,
                    },
                ],
            }
        ],
        "metadata": {"total_hits": 5881},
        "links": [
            {
                "rel": "next",
                "prompt": "Next",
                "href": "https://images-api.nasa.gov/search?q=Apollo+11&page=2",
            }
        ],
    }
}

AUDIO_SEARCH_RESPONSE = {
    "collection": {
        "version": "1.1",
        "href": "https://images-api.nasa.gov/search?media_type=audio",
        "items": [
            {
                "href": "https://images-assets.nasa.gov/audio/Ep392/collection.json",
                "data": [
                    {
                        "nasa_id": "Ep392",
                        "title": "Houston We Have a Podcast Ep. 392",
                        "media_type": "audio",
                        "date_created": "2024-01-01T00:00:00Z",
                        "center": "JSC",
                        "description": "Episode 392.",
                        "keywords": ["podcast"],
                    }
                ],
                # audio items have no links[]
            }
        ],
        "metadata": {"total_hits": 1},
    }
}

ASSET_RESPONSE = {
    "collection": {
        "version": "1.1",
        "href": f"https://images-api.nasa.gov/asset/{NASA_ID}",
        "items": [
            {"href": f"https://images-assets.nasa.gov/image/{NASA_ID}/{NASA_ID}~orig.jpg"},
            {"href": f"https://images-assets.nasa.gov/image/{NASA_ID}/{NASA_ID}~large.jpg"},
            {"href": f"https://images-assets.nasa.gov/image/{NASA_ID}/{NASA_ID}~thumb.jpg"},
            {"href": f"https://images-assets.nasa.gov/image/{NASA_ID}/metadata.json"},
        ],
    }
}

LOCATION_RESPONSE = {
    "location": f"https://images-assets.nasa.gov/image/{NASA_ID}/metadata.json"
}

CAPTIONS_RESPONSE = {
    "location": "https://images-assets.nasa.gov/video/SomeVideo/SomeVideo.srt"
}


class TestImageLibraryService:

    def test_no_api_key_required(self) -> None:
        service = ImageLibraryService()
        assert service.host == "https://images-api.nasa.gov"
        assert "api_key" not in (service.session.params or {})

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE)
    def test_search_returns_response(self, _) -> None:
        result = ImageLibraryService().search(ImageLibrarySearchRequest(q="Apollo 11"))
        assert result.collection.metadata.total_hits == 5881
        assert len(result.collection.items) == 1

    @patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE)
    def test_search_item_metadata(self, _) -> None:
        item = ImageLibraryService().search().collection.items[0]
        assert item.metadata.nasa_id == NASA_ID
        assert item.metadata.title == "Apollo 11 Mission image - Astronaut Edwin Aldrin"
        assert item.metadata.media_type == "image"
        assert item.metadata.photographer == "Neil Armstrong"
        assert item.metadata.keywords == ["Apollo 11", "Moon landing"]

    @patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE)
    def test_search_item_thumbnail(self, _) -> None:
        item = ImageLibraryService().search().collection.items[0]
        assert item.thumbnail == f"https://images-assets.nasa.gov/image/{NASA_ID}/{NASA_ID}~thumb.jpg"

    @patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE)
    def test_search_pagination_next_page(self, _) -> None:
        coll = ImageLibraryService().search().collection
        assert coll.next_page == "https://images-api.nasa.gov/search?q=Apollo+11&page=2"
        assert coll.prev_page is None

    @patch.object(BaseAPI, "get_request", return_value=AUDIO_SEARCH_RESPONSE)
    def test_audio_item_has_no_links(self, _) -> None:
        item = ImageLibraryService().search().collection.items[0]
        assert item.links is None
        assert item.thumbnail is None

    # ------------------------------------------------------------------
    # asset
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=ASSET_RESPONSE)
    def test_asset_urls(self, _) -> None:
        result = ImageLibraryService().asset(NASA_ID)
        assert len(result.urls) == 4
        assert any("orig.jpg" in url for url in result.urls)
        assert any("metadata.json" in url for url in result.urls)

    # ------------------------------------------------------------------
    # metadata and captions
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=LOCATION_RESPONSE)
    def test_metadata_returns_url(self, _) -> None:
        url = ImageLibraryService().metadata(NASA_ID)
        assert url == f"https://images-assets.nasa.gov/image/{NASA_ID}/metadata.json"

    @patch.object(BaseAPI, "get_request", return_value=CAPTIONS_RESPONSE)
    def test_captions_returns_url(self, _) -> None:
        url = ImageLibraryService().captions("SomeVideo")
        assert url.endswith(".srt")

    # ------------------------------------------------------------------
    # album
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE)
    def test_album_returns_search_response(self, _) -> None:
        result = ImageLibraryService().album("Apollo-at-50")
        assert result.collection.metadata.total_hits == 5881
