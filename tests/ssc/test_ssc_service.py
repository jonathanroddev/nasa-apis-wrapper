import datetime
from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, SSCService
from nasa_apis_wrapper import (
    SSCLocationsRequest,
    SSCTimeInterval,
    SSCSatellite,
    SSCCoordinateOption,
    SSCOutputOptions,
)

OBSERVATORIES_RESPONSE = {
    "Observatory": [
        {
            "Id": "ace",
            "Name": "ACE",
            "Resolution": 720,
            "StartTime": "1997-08-25T17:48:00.000Z",
            "EndTime": "2026-07-27T23:49:00.000Z",
            "ResourceId": "spase://SMWG/Observatory/ACE",
            "GroupId": [],
        },
        {
            "Id": "iss",
            "Name": "ISS",
            "Resolution": 60,
            "StartTime": "1998-11-21T00:00:00.000Z",
            "EndTime": "2026-07-27T23:00:00.000Z",
            "ResourceId": "spase://SMWG/Observatory/ISS",
            "GroupId": [],
        },
    ]
}

GROUND_STATIONS_RESPONSE = {
    "GroundStation": [
        {
            "Id": "GSFC",
            "Name": "Goddard Space Flight Center",
            "Location": {"Latitude": 39.0, "Longitude": -76.84},
        },
        {
            "Id": "SPA",
            "Name": "South Pole",
            "Location": {"Latitude": -89.99, "Longitude": -13.32},
        },
    ]
}

LOCATIONS_RESPONSE = {
    "StatusCode": "Success",
    "StatusSubCode": "Success",
    "StatusText": [],
    "Data": [
        {
            "Id": "ace",
            "Time": [
                "2023-01-01T00:00:00.000Z",
                "2023-01-01T00:12:00.000Z",
            ],
            "Coordinates": [
                {
                    "CoordinateSystem": "Gse",
                    "X": [1422543.0, 1422601.0],
                    "Y": [211126.0, 211098.0],
                    "Z": [45527.0, 45518.0],
                    "Latitude": [1.80, 1.79],
                    "Longitude": [8.44, 8.44],
                    "LocalTime": [12.608, 12.607],
                }
            ],
            "RadialLength": [1441385.0, 1441444.0],
        }
    ],
}

CONJUNCTIONS_RESPONSE = {
    "StatusCode": "Success",
    "StatusSubCode": "Success",
    "StatusText": [],
    "Conjunction": [
        {
            "TimeInterval": {
                "Start": "2023-01-01T01:23:00.000Z",
                "End": "2023-01-01T01:45:00.000Z",
            },
            "SatelliteDescription": [
                {"Id": "iss", "Location": {"Latitude": 39.5, "Longitude": -76.2}}
            ],
        }
    ],
}

FILES_RESPONSE = {
    "StatusCode": "Success",
    "StatusSubCode": "Success",
    "StatusText": [],
    "Files": [
        {
            "Name": "https://sscweb.gsfc.nasa.gov/tmp/orbit_plot_abc123.png",
            "MimeType": "image/png",
            "Length": 84320,
            "LastModified": "2023-01-01T12:00:00.000Z",
        }
    ],
}


class TestSSCService:

    def test_no_api_key_required(self) -> None:
        service = SSCService()
        assert service.host == "https://sscweb.gsfc.nasa.gov/WS/sscr/2"
        assert "api_key" not in (service.session.params or {})

    # ------------------------------------------------------------------
    # observatories
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=OBSERVATORIES_RESPONSE)
    def test_observatories_returns_list(self, _) -> None:
        result = SSCService().observatories()
        assert len(result) == 2
        assert result[0].Id == "ace"
        assert result[0].Resolution == 720
        assert isinstance(result[0].StartTime, datetime.datetime)

    @patch.object(BaseAPI, "get_request", return_value=OBSERVATORIES_RESPONSE)
    def test_observatories_filter_by_id(self, _) -> None:
        result = SSCService().observatories(id="ace")
        assert result[0].Name == "ACE"

    # ------------------------------------------------------------------
    # ground_stations
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=GROUND_STATIONS_RESPONSE)
    def test_ground_stations(self, _) -> None:
        result = SSCService().ground_stations()
        assert len(result) == 2
        assert result[0].Id == "GSFC"
        assert result[0].Location.Latitude == 39.0

    # ------------------------------------------------------------------
    # locations_get
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=LOCATIONS_RESPONSE)
    def test_locations_get(self, _) -> None:
        result = SSCService().locations_get(
            satellites=["ace"],
            start=datetime.datetime(2023, 1, 1),
            end=datetime.datetime(2023, 1, 1, 6),
            coord_systems=["Gse"],
        )
        assert result.StatusCode == "Success"
        assert len(result.Data) == 1
        sat = result.Data[0]
        assert sat.Id == "ace"
        assert len(sat.Time) == 2
        assert sat.Coordinates[0].CoordinateSystem == "Gse"
        assert sat.Coordinates[0].X[0] == 1422543.0
        assert sat.RadialLength[0] == 1441385.0

    @patch.object(BaseAPI, "get_request", return_value=LOCATIONS_RESPONSE)
    def test_locations_get_datetime_format_in_path(self, mock_get) -> None:
        SSCService().locations_get(
            satellites="ace",
            start=datetime.datetime(2023, 1, 1, 0, 0, 0),
            end=datetime.datetime(2023, 1, 1, 6, 0, 0),
            coord_systems="Gse",
        )
        call_args = mock_get.call_args
        endpoint = call_args[0][0]
        assert "20230101T000000Z" in endpoint
        assert "20230101T060000Z" in endpoint

    # ------------------------------------------------------------------
    # locations (POST)
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "post_request", return_value=LOCATIONS_RESPONSE)
    def test_locations_post(self, _) -> None:
        request = SSCLocationsRequest(
            TimeInterval=SSCTimeInterval(
                Start="2023-01-01T00:00:00Z",
                End="2023-01-01T06:00:00Z",
            ),
            Satellites=[SSCSatellite(Id="ace")],
            OutputOptions=SSCOutputOptions(
                CoordinateOptions=[
                    SSCCoordinateOption(CoordinateSystem="Gse", Component="X"),
                    SSCCoordinateOption(CoordinateSystem="Gse", Component="Y"),
                ]
            ),
        )
        result = SSCService().locations(request)
        assert result.StatusCode == "Success"
        assert result.Data[0].Id == "ace"

    # ------------------------------------------------------------------
    # conjunctions
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "post_request", return_value=CONJUNCTIONS_RESPONSE)
    def test_conjunctions(self, _) -> None:
        result = SSCService().conjunctions({
            "TimeInterval": {"Start": "2023-01-01T00:00:00Z", "End": "2023-01-02T00:00:00Z"},
            "ConditionOperator": "Any",
            "Conditions": [
                {"@type": "SatelliteCondition", "Satellites": [{"Id": "iss"}], "MinimumNumber": 1}
            ],
        })
        assert result.StatusCode == "Success"
        assert len(result.Conjunction) == 1
        c = result.Conjunction[0]
        assert isinstance(c.TimeInterval.Start, datetime.datetime)

    # ------------------------------------------------------------------
    # graphs and kml
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "post_request", return_value=FILES_RESPONSE)
    def test_graphs_returns_file_url(self, _) -> None:
        result = SSCService().graphs({
            "TimeInterval": {"Start": "2023-01-01T00:00:00Z", "End": "2023-01-01T06:00:00Z"},
            "Satellites": [{"Id": "ace"}],
            "GraphOptions": {"@type": "OrbitGraphOptions", "CoordinateSystem": "Gse"},
        })
        assert result.Files[0].Name.endswith(".png")
        assert result.Files[0].MimeType == "image/png"

    @patch.object(BaseAPI, "post_request", return_value=FILES_RESPONSE)
    def test_kml(self, _) -> None:
        result = SSCService().kml({
            "TimeInterval": {"Start": "2023-01-01T00:00:00Z", "End": "2023-01-01T06:00:00Z"},
            "Satellites": [{"Id": "iss"}],
            "Trajectory": True,
        })
        assert result.StatusCode == "Success"
