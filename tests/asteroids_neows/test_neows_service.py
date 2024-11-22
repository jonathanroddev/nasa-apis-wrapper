import json
from unittest.mock import patch

import pytest

from nasa_apis_wrapper import BaseAPI, NeoWsService


def generate_near_earth_object_item(bad_format=False):
    near_earth_object_item = {
        "links": {
            "self": "self_link"
        },
        "id": "2482505",
        "neo_reference_id": "2482505",
        "name": "482505 (2012 TQ78)",
        "nasa_jpl_url": "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=2482505",
        "absolute_magnitude_h": 19.53,
        "estimated_diameter": {
            "kilometers": {
                "estimated_diameter_min": 0.3300311834,
                "estimated_diameter_max": 0.7379721607
            },
            "meters": {
                "estimated_diameter_min": 330.0311833581,
                "estimated_diameter_max": 737.9721606833
            },
            "miles": {
                "estimated_diameter_min": 0.2050718064,
                "estimated_diameter_max": 0.4585544995
            },
            "feet": {
                "estimated_diameter_min": 1082.7795076085,
                "estimated_diameter_max": 2421.1685836563
            }
        },
        "is_potentially_hazardous_asteroid": "false",
        "close_approach_data": [
            {
                "close_approach_date": "2024-11-29",
                "close_approach_date_full": "2024-Nov-29 04:17",
                "epoch_date_close_approach": 1732853820000,
                "relative_velocity": {
                    "kilometers_per_second": "22.10134715",
                    "kilometers_per_hour": "79564.8497401253",
                    "miles_per_hour": "49438.5034399128"
                },
                "miss_distance": {
                    "astronomical": "0.3575462444",
                    "lunar": "139.0854890716",
                    "kilometers": "53488156.588739428",
                    "miles": "33235999.3304749864"
                },
                "orbiting_body": "Earth"
            }
        ],
        "is_sentry_object": "false"
    }
    if bad_format:
        near_earth_object_item["estimated_diameter"]["bad_diameter"] = "bad"
    return near_earth_object_item


class TestNeoWsService:

    @patch.object(BaseAPI, "get_request", return_value=json.dumps(
        {
            "links": {
                "next": "next",
                "previous": "previous",
                "self": "self"
            },
            "element_count": 94,
            "near_earth_objects": {
                "2022-03-27": [
                    generate_near_earth_object_item(),
                ]
            }
        }
    ))
    def test_feed(self, get_request) -> None:
        neows_service: NeoWsService = NeoWsService("api_key")
        result = neows_service.feed()
        assert result

    @patch.object(BaseAPI, "get_request", return_value=json.dumps(
        {
            "links": {
                "next": "next",
                "previous": "previous",
                "self": "self"
            },
            "element_count": 94,
            "near_earth_objects": {
                "wrong_key": [
                    generate_near_earth_object_item(),
                ]
            }
        }
    ))
    def test_feed_should_raise_value_error(self, get_request) -> None:
        neows_service: NeoWsService = NeoWsService("api_key")
        with pytest.raises(ValueError):
            result = neows_service.feed()

    @patch.object(BaseAPI, "get_request", return_value=json.dumps(
        generate_near_earth_object_item()
    ))
    def test_lookup(self, get_request) -> None:
        neows_service: NeoWsService = NeoWsService("api_key")
        result = neows_service.lookup("1")
        assert result

    @patch.object(BaseAPI, "get_request", return_value=json.dumps(
        generate_near_earth_object_item(bad_format=True)
    ))
    def test_lookup_should_raise_value_error(self, get_request) -> None:
        neows_service: NeoWsService = NeoWsService("api_key")
        with pytest.raises(ValueError):
            result = neows_service.lookup("1")

    @patch.object(BaseAPI, "get_request", return_value=json.dumps(
        {
            "links": {
                "next": "next",
                "previous": "previous",
                "self": "self"
            },
            "page": {
                "size": 1,
                "total_elements": 1,
                "total_pages": 1,
                "number": 1
            },
            "near_earth_objects": [
                generate_near_earth_object_item(),
            ]
        }
    ))
    def test_browse(self, get_request) -> None:
        neows_service: NeoWsService = NeoWsService("api_key")
        result = neows_service.browse()
        assert result
