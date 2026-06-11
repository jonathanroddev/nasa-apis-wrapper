from unittest.mock import patch

import pytest

from nasa_apis_wrapper import BaseAPI, ExoplanetService
from nasa_apis_wrapper import NasaAPIException


def make_planet(**overrides) -> dict:
    base = {
        "pl_name": "51 Peg b",
        "hostname": "51 Peg",
        "pl_letter": "b",
        "discoverymethod": "Radial Velocity",
        "disc_year": 1995,
        "pl_orbper": 4.23078500,
        "pl_bmasse": 146.2018,
        "pl_bmassj": 0.4603,
        "pl_rade": 14.3,
        "pl_radj": 1.27,
        "st_teff": 5758.0,
        "st_mass": 1.03,
        "st_rad": 1.175,
        "sy_dist": 15.46,
        "sy_pnum": 1,
        "ra": 344.3675,
        "dec": 20.7690,
        "tran_flag": 0,
        "rv_flag": 1,
        # extra columns that ExoplanetRecord should silently ignore
        "pl_bmasse_reflink": "<a href='...'/>",
        "pl_orbpererr1": 0.00000200,
        "pl_orbpererr2": -0.00000200,
    }
    base.update(overrides)
    return base


class TestExoplanetService:

    def test_no_api_key_required(self) -> None:
        service = ExoplanetService()
        assert service.host == "https://exoplanetarchive.ipac.caltech.edu/TAP"
        assert "api_key" not in (service.session.params or {})

    # ------------------------------------------------------------------
    # _build_query
    # ------------------------------------------------------------------

    def test_build_query_minimal(self) -> None:
        adql = ExoplanetService._build_query("pscomppars", None, None, None, None)
        assert adql == "SELECT * FROM pscomppars"

    def test_build_query_with_all_options(self) -> None:
        adql = ExoplanetService._build_query(
            "ps",
            ["pl_name", "pl_masse"],
            "default_flag = 1",
            "pl_masse DESC",
            10,
        )
        assert adql == "SELECT TOP 10 pl_name, pl_masse FROM ps WHERE default_flag = 1 ORDER BY pl_masse DESC"

    def test_build_query_limit_only(self) -> None:
        adql = ExoplanetService._build_query("pscomppars", None, None, None, 5)
        assert adql == "SELECT TOP 5 * FROM pscomppars"

    # ------------------------------------------------------------------
    # query (raw)
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=[make_planet()])
    def test_query_returns_list_of_dicts(self, _) -> None:
        result = ExoplanetService().query("SELECT * FROM pscomppars")
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert result[0]["pl_name"] == "51 Peg b"

    # ------------------------------------------------------------------
    # planets
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=[make_planet()])
    def test_planets_returns_typed_records(self, _) -> None:
        result = ExoplanetService().planets()
        assert len(result) == 1
        assert result[0].pl_name == "51 Peg b"
        assert result[0].disc_year == 1995
        assert result[0].rv_flag == 1

    @patch.object(BaseAPI, "get_request", return_value=[make_planet()])
    def test_planets_extra_columns_ignored(self, _) -> None:
        result = ExoplanetService().planets()
        assert not hasattr(result[0], "pl_bmasse_reflink")
        assert not hasattr(result[0], "pl_orbpererr1")

    # ------------------------------------------------------------------
    # planet (single)
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=[make_planet()])
    def test_planet_found(self, _) -> None:
        result = ExoplanetService().planet("51 Peg b")
        assert result.pl_name == "51 Peg b"
        assert result.hostname == "51 Peg"

    @patch.object(BaseAPI, "get_request", return_value=[])
    def test_planet_not_found_raises(self, _) -> None:
        with pytest.raises(NasaAPIException, match="not found"):
            ExoplanetService().planet("Nonexistent Planet z")

    # ------------------------------------------------------------------
    # confirmed_planets
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=[make_planet(), make_planet(pl_name="HD 209458 b", hostname="HD 209458")])
    def test_confirmed_planets(self, _) -> None:
        result = ExoplanetService().confirmed_planets()
        assert len(result) == 2

    # ------------------------------------------------------------------
    # planets_by_method
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=[make_planet(discoverymethod="Transit", tran_flag=1)])
    def test_planets_by_method(self, _) -> None:
        result = ExoplanetService().planets_by_method("Transit")
        assert result[0].discoverymethod == "Transit"
        assert result[0].tran_flag == 1
