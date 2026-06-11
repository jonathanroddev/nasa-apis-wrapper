from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, EONETService


def make_event() -> dict:
    return {
        "id": "EONET_20098",
        "title": "Eagle Lake Fire",
        "description": None,
        "link": "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_20098",
        "closed": None,
        "categories": [{"id": "wildfires", "title": "Wildfires"}],
        "sources": [{"id": "IRWIN", "url": "https://irwin.doi.gov/incident/1"}],
        "geometry": [
            {
                "magnitudeValue": 550.0,
                "magnitudeUnit": "acres",
                "date": "2026-05-14T11:04:00Z",
                "type": "Point",
                "coordinates": [-93.72348843, 43.11279415],
            }
        ],
    }


EVENTS_RESPONSE = {
    "title": "EONET Events",
    "description": "Natural events from EONET.",
    "link": "https://eonet.gsfc.nasa.gov/api/v3/events",
    "events": [make_event()],
}

GEOJSON_RESPONSE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": "EONET_20098",
                "title": "Eagle Lake Fire",
                "description": None,
                "link": "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_20098/geojson",
                "closed": None,
                "date": "2026-05-14T11:04:00Z",
                "magnitudeValue": 550.0,
                "magnitudeUnit": "acres",
                "categories": [{"id": "wildfires", "title": "Wildfires"}],
                "sources": [{"id": "IRWIN", "url": "https://irwin.doi.gov/incident/1"}],
            },
            "geometry": {"type": "Point", "coordinates": [-93.72, 43.11]},
        }
    ],
}

CATEGORIES_RESPONSE = {
    "title": "EONET Event Categories",
    "description": "List of all categories.",
    "link": "https://eonet.gsfc.nasa.gov/api/v3/categories",
    "categories": [
        {
            "id": "wildfires",
            "title": "Wildfires",
            "link": "https://eonet.gsfc.nasa.gov/api/v3/categories/wildfires",
            "description": "Wildfires are uncontrolled fires.",
            "layers": "https://eonet.gsfc.nasa.gov/api/v3/layers/wildfires",
        }
    ],
}

SOURCES_RESPONSE = {
    "title": "EONET Event Sources",
    "description": "List of all sources.",
    "link": "https://eonet.gsfc.nasa.gov/api/v3/sources",
    "sources": [
        {
            "id": "IRWIN",
            "title": "Integrated Reporting of Wildland-Fire Information",
            "source": "https://irwin.doi.gov/",
            "link": "https://eonet.gsfc.nasa.gov/api/v3/events?source=IRWIN",
        }
    ],
}

MAGNITUDES_RESPONSE = {
    "title": "EONET Event Magnitudes",
    "description": "List of all magnitudes.",
    "link": "https://eonet.gsfc.nasa.gov/api/v3/magnitudes",
    "magnitudes": [
        {
            "id": "ac",
            "name": "Acres",
            "unit": "acres",
            "description": "An area measurement in acres.",
            "link": "https://eonet.gsfc.nasa.gov/api/v3/events?magID=ac",
        }
    ],
}

LAYERS_RESPONSE = {
    "title": "EONET Web Service Layers",
    "description": "List of web service layers.",
    "link": "https://eonet.gsfc.nasa.gov/api/v3/layers",
    "categories": [
        {
            "id": "wildfires",
            "title": "Wildfires",
            "layers": [
                {
                    "name": "AIRS_CO_Total_Column_Day",
                    "serviceUrl": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/",
                    "serviceTypeId": "WMTS_1_0_0",
                    "parameters": [{"TILEMATRIXSET": "2km", "FORMAT": "image/png"}],
                }
            ],
        }
    ],
}


class TestEONETService:

    def test_no_api_key_required(self) -> None:
        service = EONETService()
        assert service.host == "https://eonet.gsfc.nasa.gov/api/v3"
        assert "api_key" not in (service.session.params or {})

    @patch.object(BaseAPI, "get_request", return_value=EVENTS_RESPONSE)
    def test_events(self, _) -> None:
        result = EONETService().events()
        assert len(result.events) == 1
        assert result.events[0].id == "EONET_20098"
        assert result.events[0].closed is None

    @patch.object(BaseAPI, "get_request", return_value=make_event())
    def test_event(self, _) -> None:
        result = EONETService().event("EONET_20098")
        assert result.id == "EONET_20098"
        assert result.geometry[0].type == "Point"
        assert result.geometry[0].magnitudeValue == 550.0

    @patch.object(BaseAPI, "get_request", return_value=GEOJSON_RESPONSE)
    def test_events_geojson(self, _) -> None:
        result = EONETService().events_geojson()
        assert result.type == "FeatureCollection"
        assert result.features[0].properties.id == "EONET_20098"

    @patch.object(BaseAPI, "get_request", return_value=CATEGORIES_RESPONSE)
    def test_categories(self, _) -> None:
        result = EONETService().categories()
        assert len(result.categories) == 1
        assert result.categories[0].id == "wildfires"

    @patch.object(BaseAPI, "get_request", return_value={**EVENTS_RESPONSE, "events": [make_event()]})
    def test_category_events(self, _) -> None:
        result = EONETService().category_events("wildfires")
        assert len(result.events) == 1

    @patch.object(BaseAPI, "get_request", return_value=SOURCES_RESPONSE)
    def test_sources(self, _) -> None:
        result = EONETService().sources()
        assert result.sources[0].id == "IRWIN"

    @patch.object(BaseAPI, "get_request", return_value=MAGNITUDES_RESPONSE)
    def test_magnitudes(self, _) -> None:
        result = EONETService().magnitudes()
        assert result.magnitudes[0].id == "ac"
        assert result.magnitudes[0].unit == "acres"

    @patch.object(BaseAPI, "get_request", return_value=LAYERS_RESPONSE)
    def test_layers(self, _) -> None:
        result = EONETService().layers()
        assert result.categories[0].layers[0].serviceTypeId == "WMTS_1_0_0"

    @patch.object(BaseAPI, "get_request", return_value=LAYERS_RESPONSE)
    def test_layers_by_category(self, _) -> None:
        result = EONETService().layers("wildfires")
        assert result.categories[0].id == "wildfires"
