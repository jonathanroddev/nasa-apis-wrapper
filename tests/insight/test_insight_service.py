from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, InsightService

MOCK_RESPONSE = {
    "675": {
        "AT": {"av": -62.314, "ct": 177556, "mn": -96.872, "mx": -15.908},
        "HWS": {"av": 4.281, "ct": 166647, "mn": 0.152, "mx": 22.024},
        "PRE": {"av": 718.641, "ct": 185464, "mn": 703.341, "mx": 730.138},
        "WD": {
            "13": {
                "compass_degrees": 292.5,
                "compass_point": "WNW",
                "compass_right": -0.923879532511,
                "compass_up": 0.382683432365,
                "ct": 30283,
            },
            "most_common": {
                "compass_degrees": 292.5,
                "compass_point": "WNW",
                "compass_right": -0.923879532511,
                "compass_up": 0.382683432365,
                "ct": 30283,
            },
        },
        "First_UTC": "2020-10-19T18:32:20Z",
        "Last_UTC": "2020-10-20T19:11:55Z",
        "Month_ordinal": 10,
        "Northern_season": "early winter",
        "Southern_season": "early summer",
        "Season": "fall",
    },
    "676": {
        "PRE": {"av": 720.1, "ct": 184000, "mn": 705.0, "mx": 731.5},
        "WD": {
            "most_common": {
                "compass_degrees": 270.0,
                "compass_point": "W",
                "compass_right": -1.0,
                "compass_up": 0.0,
                "ct": 12000,
            },
        },
        "First_UTC": "2020-10-20T19:12:00Z",
        "Last_UTC": "2020-10-21T19:51:35Z",
        "Month_ordinal": 10,
        "Northern_season": "early winter",
        "Southern_season": "early summer",
        "Season": "fall",
    },
    "sol_keys": ["675", "676"],
    "validity_checks": {
        "675": {
            "AT": {"sol_hours_with_data": list(range(24)), "valid": True},
            "HWS": {"sol_hours_with_data": list(range(24)), "valid": True},
            "PRE": {"sol_hours_with_data": list(range(24)), "valid": True},
            "WD": {"sol_hours_with_data": list(range(24)), "valid": True},
        },
        "676": {
            "AT": {"sol_hours_with_data": [0], "valid": False},
            "HWS": {"sol_hours_with_data": [0], "valid": False},
            "PRE": {"sol_hours_with_data": list(range(18)), "valid": True},
            "WD": {"sol_hours_with_data": list(range(18)), "valid": True},
        },
        "sol_hours_required": 18,
        "sols_checked": ["674", "675", "676"],
    },
}


class TestInsightService:

    @patch.object(BaseAPI, "get_request", return_value=MOCK_RESPONSE)
    def test_weather_returns_response(self, _) -> None:
        result = InsightService("api_key").weather()
        assert result.sol_keys == ["675", "676"]
        assert "675" in result.sols
        assert "676" in result.sols

    @patch.object(BaseAPI, "get_request", return_value=MOCK_RESPONSE)
    def test_sol_data_sensors(self, _) -> None:
        sol = InsightService("api_key").weather().sols["675"]
        assert sol.AT.av == -62.314
        assert sol.AT.mn == -96.872
        assert sol.PRE.ct == 185464
        assert sol.Season == "fall"
        assert sol.Northern_season == "early winter"

    @patch.object(BaseAPI, "get_request", return_value=MOCK_RESPONSE)
    def test_optional_sensors_absent(self, _) -> None:
        # Sol 676 has no AT or HWS in mock
        sol = InsightService("api_key").weather().sols["676"]
        assert sol.AT is None
        assert sol.HWS is None
        assert sol.PRE is not None

    @patch.object(BaseAPI, "get_request", return_value=MOCK_RESPONSE)
    def test_wind_direction_parsed(self, _) -> None:
        wd = InsightService("api_key").weather().sols["675"].WD
        assert wd.most_common.compass_point == "WNW"
        assert "13" in wd.sectors
        assert wd.sectors["13"].compass_degrees == 292.5

    @patch.object(BaseAPI, "get_request", return_value=MOCK_RESPONSE)
    def test_validity_checks(self, _) -> None:
        vc = InsightService("api_key").weather().validity_checks
        assert vc.sol_hours_required == 18
        assert "675" in vc.sols_checked
        assert vc.sol_validity["675"].AT.valid is True
        assert vc.sol_validity["676"].AT.valid is False

    @patch.object(BaseAPI, "get_request", return_value=MOCK_RESPONSE)
    def test_dynamic_keys_not_leaked_into_sols(self, _) -> None:
        result = InsightService("api_key").weather()
        assert "sol_keys" not in result.sols
        assert "validity_checks" not in result.sols
