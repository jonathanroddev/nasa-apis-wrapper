from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, CNEOSService
from nasa_apis_wrapper import (
    FireballRequest,
    CADRequest,
    SentryRequest,
    SBIdentRequest,
    SBRadarRequest,
    SBSatellitesRequest,
    MDesignAccessibleRequest,
    MDesignMapRequest,
    SBObsRequest,
)

FIREBALL_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL CNEOS"},
    "count": 2,
    "fields": ["date", "lat", "lat-dir", "lon", "lon-dir", "alt", "vel", "energy", "impact-e"],
    "data": [
        ["2022-01-15 15:35:00", "29.0", "N", "88.0", "E", "35.0", "21.5", "4.6", "1.5"],
        ["2022-03-11 21:21:00", None, None, None, None, None, "18.3", "1.9", "0.4"],
    ],
}

CAD_RESPONSE = {
    "signature": {"version": "1.3", "source": "NASA/JPL CNEOS"},
    "count": "1",
    "total": "5881",
    "fields": ["des", "orbit_id", "jd", "cd", "dist", "dist_min", "dist_max", "v_rel", "v_inf", "t_sigma_f", "h"],
    "data": [
        ["99942", "207", "2462240.40625", "2029-Apr-13 21:46", "0.000254", "0.000254", "0.000255", "7.42", "5.87", "0 00:01", "19.7"],
    ],
}

CAD_EMPTY_RESPONSE = {
    "signature": {"version": "1.3", "source": "NASA/JPL CNEOS"},
    "count": 0,
}

SENTRY_RESPONSE = {
    "signature": {"version": "1.3", "source": "NASA/JPL Sentry"},
    "count": "2",
    "data": [
        {
            "des": "29075",
            "diameter": "0.503",
            "fullname": "(29075) 1950 DA",
            "h": "17.6",
            "id": "bJ50D00A",
            "ip": "7.18e-04",
            "last_obs": "2012-12-31",
            "last_obs_jd": "2456292.5",
            "n_imp": 1,
            "ps_cum": "-1.42",
            "ps_max": "-1.42",
            "range": "2880-2880",
            "ts_max": "0",
            "v_inf": "13.90",
        },
        {
            "des": "99942",
            "diameter": None,
            "fullname": "99942 Apophis (2004 MN4)",
            "h": "19.7",
            "id": "bK04M04N",
            "ip": "2.3e-05",
            "last_obs": "2021-03-25",
            "last_obs_jd": "2459298.5",
            "n_imp": 5,
            "ps_cum": "-3.7",
            "ps_max": "-3.7",
            "range": "2068-2103",
            "ts_max": "0",
            "v_inf": "5.87",
        },
    ],
}

SCOUT_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL Scout"},
    "count": "1",
    "data": [
        {
            "objectName": "P10vY9r",
            "nObs": 8,
            "arc": "0.23",
            "rmsN": "0.52",
            "H": "27.3",
            "rating": "5",
            "moid": "0.0012",
            "caDist": "0.0024",
            "vInf": "4.5",
            "phaScore": 0,
            "neoScore": 99,
            "geocentricScore": 0,
            "ieoScore": 0,
            "tisserandScore": 0,
            "lastRun": "2022-01-15 12:00:00",
            "ra": "123.4",
            "dec": "-5.6",
            "elong": "145.2",
            "rate": "0.24",
            "Vmag": "21.3",
            "unc": "0.15",
            "uncP1": "0.30",
        }
    ],
}

NHATS_RESPONSE = {
    "signature": {"version": "2.0", "source": "NASA/JPL NHATS"},
    "count": 1,
    "data": [
        {
            "des": "2015 JD3",
            "fullname": "(2015 JD3)",
            "orbit_id": "31",
            "h": "22.8",
            "min_size": "0.041",
            "max_size": "0.092",
            "size": None,
            "size_sigma": None,
            "occ": "0",
            "min_dv": {"dv": "4.81", "dur": 450},
            "min_dur": {"dv": "5.23", "dur": 365},
            "n_via_traj": 248,
            "obs_start": "2015-04-25",
            "obs_end": "2016-06-30",
            "obs_mag": "24.2",
            "obs_flag": "Y",
            "radar_obs_a": None,
            "radar_snr_a": None,
            "radar_obs_g": None,
            "radar_snr_g": None,
        }
    ],
}

SBDB_QUERY_RESPONSE = {
    "count": 2,
    "data": [
        {"pdes": "433", "name": "Eros", "H": "10.43", "neo": "1"},
        {"pdes": "1862", "name": "Apollo", "H": "16.25", "neo": "1"},
    ],
}

JD_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL SSD"},
    "jd": "2451545.0000000",
    "cd": "2000-Jan-01 12:00:00",
    "year": 2000,
    "month": "01",
    "month_name": "Jan",
    "doy": 1,
    "dow": "7",
    "dow_name": "Saturday",
    "day_and_time": "2000-Jan-01 12:00:00",
}

CD_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL SSD"},
    "jd": "2451545.0000000",
}

SBIDENT_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL SSD"},
    "observer": {"obs_date": "2024-01-15 06:00:00", "fov_center": "10h30m +20d00m"},
    "n_first_pass": 2,
    "n_second_pass": 0,
    "fields_first": ["Designation", "RA", "Dec", "Vmag"],
    "fields_second": [],
    "data_first_pass": [
        ["(2024 AB)", "10 30 12.3", "+19 58 44", "21.5"],
        ["(2022 XY1)", "10 29 55.1", "+20 01 32", "20.1"],
    ],
    "data_second_pass": [],
}

SBRADAR_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL SSD"},
    "count": "2",
    "fields": ["des", "epoch", "value", "sigma", "units", "freq", "rcvr", "xmit", "bp"],
    "data": [
        ["433", "1975-01-28 00:00:00", 4800000.0, 50000.0, "us", 2380.0, "GBT", "GBT", "C"],
        ["433", "1975-01-29 00:00:00", 4750000.0, 45000.0, "us", 2380.0, "GBT", "GBT", "C"],
    ],
}

SBSAT_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL SSD"},
    "count": "1",
    "data": [
        {
            "sat": {
                "pdes": "243",
                "confirmed": "Y",
                "prov_year": "1993",
                "prov_num": "1",
                "iau_num": "1",
                "iau_name": "Dactyl",
                "sat_fullname": "(243) Ida I Dactyl",
                "ref": "IAU-MPC",
                "notes": None,
                "kind": "a",
                "prefix": None,
            },
            "orbit": {
                "oid": "1",
                "epoch": None,
                "frame": "equatorial",
                "equinox": "J2000",
                "e": "0.0",
                "a": "108.0",
                "i": "0.0",
                "om": "0.0",
                "per": "20.0",
                "ref": "Belton et al. 1996",
                "notes": None,
            },
            "phys_par": None,
        }
    ],
}

MDESIGN_ACCESSIBLE_RESPONSE = {
    "signature": {"version": "2.0", "source": "NASA/JPL SSD"},
    "fields": ["name", "date0", "MJD0", "datef", "MJDF", "c3_dep", "vinf_dep", "vinf_arr", "dv_tot", "tof", "class", "H"],
    "constraints": {"lim": 200, "year": "2024", "crit": 1},
    "records": [
        ["(2015 JD3)", "2024-Mar-15", 60384.5, "2025-Feb-10", 60751.5, 2.1, 1.5, 1.8, 4.2, 366, "AMO", "22.8"],
    ],
}

SBOBS_RESPONSE = {
    "signature": {"version": "1.0", "source": "NASA/JPL SSD"},
    "lat": 19.82, "lon": -155.47, "alt": 4.2,
    "total_objects": 150,
    "shown_objects": 12,
    "fields": ["Designation", "Rise time (UT)", "Transit time (UT)", "Vmag", "Elong."],
    "data": [
        ["(433) Eros", "22:15", "02:30", "12.5", "145.2"],
        ["(4179) Toutatis", "23:40", "04:10", "15.3", "120.8"],
    ],
    "obs_night": {
        "sun_set": "18:30",
        "sun_rise": "06:15",
        "dark_time": "08:45",
        "begin_astronomical": "2024-06-15 19:00",
        "end_astronomical": "2024-06-16 05:45",
        "moon_rise": "2024-06-15 23:10",
        "moon_set": "2024-06-16 08:40",
        "transit_phase": "0.72",
    },
}


class TestCNEOSService:

    def test_no_api_key_required(self) -> None:
        service = CNEOSService()
        assert service.host == "https://ssd-api.jpl.nasa.gov"
        assert "api_key" not in (service.session.params or {})

    # ------------------------------------------------------------------
    # Fireball
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=FIREBALL_RESPONSE)
    def test_fireballs_records(self, _) -> None:
        result = CNEOSService().fireballs()
        assert result.count == 2
        assert len(result.records) == 2
        first = result.records[0]
        assert first["date"] == "2022-01-15 15:35:00"
        assert first["energy"] == "4.6"

    @patch.object(BaseAPI, "get_request", return_value=FIREBALL_RESPONSE)
    def test_fireballs_nullable_location(self, _) -> None:
        result = CNEOSService().fireballs()
        assert result.records[1]["lat"] is None
        assert result.records[1]["lon"] is None

    @patch.object(BaseAPI, "get_request", return_value=FIREBALL_RESPONSE)
    def test_fireballs_request_serializes_aliases(self, mock_get) -> None:
        CNEOSService().fireballs(FireballRequest(date_min="2020-01-01", limit=10))
        call_params = mock_get.call_args[1]["params"]
        assert "date-min" in call_params
        assert "limit" in call_params

    # ------------------------------------------------------------------
    # CAD
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=CAD_RESPONSE)
    def test_close_approaches_records(self, _) -> None:
        result = CNEOSService().close_approaches()
        assert result.count == "1"
        assert len(result.records) == 1
        ca = result.records[0]
        assert ca["des"] == "99942"
        assert ca["cd"] == "2029-Apr-13 21:46"
        assert ca["dist"] == "0.000254"

    @patch.object(BaseAPI, "get_request", return_value=CAD_EMPTY_RESPONSE)
    def test_close_approaches_empty(self, _) -> None:
        result = CNEOSService().close_approaches()
        assert result.count == "0"
        assert result.records == []

    # ------------------------------------------------------------------
    # Sentry
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SENTRY_RESPONSE)
    def test_sentry_summary(self, _) -> None:
        result = CNEOSService().sentry_summary()
        assert len(result) == 2
        assert result[0].des == "29075"
        assert result[0].ps_max == "-1.42"
        assert result[0].diameter == "0.503"
        assert result[1].diameter is None

    # ------------------------------------------------------------------
    # Scout
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SCOUT_RESPONSE)
    def test_scout_summary(self, _) -> None:
        result = CNEOSService().scout_summary()
        assert len(result) == 1
        assert result[0].objectName == "P10vY9r"
        assert result[0].neoScore == 99

    # ------------------------------------------------------------------
    # NHATS
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=NHATS_RESPONSE)
    def test_nhats_summary(self, _) -> None:
        result = CNEOSService().nhats_summary()
        assert len(result) == 1
        obj = result[0]
        assert obj.des == "2015 JD3"
        assert obj.min_dv.dv == "4.81"
        assert obj.min_dur.dur == 365
        assert obj.size is None

    # ------------------------------------------------------------------
    # SBDB Query
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SBDB_QUERY_RESPONSE)
    def test_query_returns_records(self, _) -> None:
        result = CNEOSService().query("pdes,name,H", neo=1, limit=2)
        assert len(result) == 2
        assert result[0]["pdes"] == "433"
        assert result[0]["name"] == "Eros"

    # ------------------------------------------------------------------
    # JD / Calendar Converter
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=JD_RESPONSE)
    def test_jd_to_date(self, _) -> None:
        result = CNEOSService().jd_to_date(2451545.0)
        assert result.jd == "2451545.0000000"
        assert result.cd == "2000-Jan-01 12:00:00"
        assert result.year == 2000
        assert result.dow_name == "Saturday"

    @patch.object(BaseAPI, "get_request", return_value=CD_RESPONSE)
    def test_date_to_jd(self, _) -> None:
        result = CNEOSService().date_to_jd("2000-01-01 12:00:00")
        assert result.jd == "2451545.0000000"
        assert result.cd is None

    # ------------------------------------------------------------------
    # SB Identification
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SBIDENT_RESPONSE)
    def test_identify(self, _) -> None:
        result = CNEOSService().identify(SBIdentRequest(
            mpc_code="568",
            obs_time="2024-01-15 06:00",
            fov_ra_center="10 30 00",
            fov_dec_center="+20 00 00",
        ))
        assert result.n_first_pass == 2
        assert result.n_second_pass == 0
        assert len(result.records_first) == 2
        assert result.records_first[0]["Designation"] == "(2024 AB)"
        assert result.records_first[0]["Vmag"] == "21.5"
        assert result.records_second == []

    # ------------------------------------------------------------------
    # SB Radar
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SBRADAR_RESPONSE)
    def test_radar_astrometry(self, _) -> None:
        result = CNEOSService().radar_astrometry(SBRadarRequest(des="433"))
        assert result.count == "2"
        assert len(result.records) == 2
        assert result.records[0]["des"] == "433"
        assert result.records[0]["units"] == "us"
        assert result.coords is None

    # ------------------------------------------------------------------
    # SB Satellites
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SBSAT_RESPONSE)
    def test_satellites(self, _) -> None:
        result = CNEOSService().satellites(SBSatellitesRequest(des="243", orb=True))
        assert result.count == "1"
        assert len(result.data) == 1
        assert result.data[0].sat["iau_name"] == "Dactyl"
        assert result.data[0].orbit["a"] == "108.0"
        assert result.data[0].phys_par is None

    # ------------------------------------------------------------------
    # Mission Design
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=MDESIGN_ACCESSIBLE_RESPONSE)
    def test_mission_design_accessible(self, _) -> None:
        result = CNEOSService().mission_design_accessible(MDesignAccessibleRequest(lim=10))
        assert len(result.records) == 1
        assert result.records[0]["name"] == "(2015 JD3)"
        assert result.records[0]["dv_tot"] == 4.2
        assert result.constraints["lim"] == 200

    @patch.object(BaseAPI, "get_request", return_value=MDESIGN_ACCESSIBLE_RESPONSE)
    def test_mission_design_query(self, _) -> None:
        result = CNEOSService().mission_design_query(des="433")
        assert isinstance(result, dict)

    @patch.object(BaseAPI, "get_request", return_value=MDESIGN_ACCESSIBLE_RESPONSE)
    def test_mission_design_map(self, _) -> None:
        result = CNEOSService().mission_design_map(MDesignMapRequest(
            des="433", mjd0=60000, span=365, tof_min=90, tof_max=450, step=5,
        ))
        assert isinstance(result, dict)

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    @patch.object(BaseAPI, "get_request", return_value=SBOBS_RESPONSE)
    def test_observability(self, _) -> None:
        result = CNEOSService().observability(SBObsRequest(
            mpc_code="568",
            obs_time="2024-06-15",
            vmag_max=18.0,
        ))
        assert result.total_objects == 150
        assert result.shown_objects == 12
        assert len(result.records) == 2
        assert result.records[0]["Designation"] == "(433) Eros"
        assert result.obs_night["dark_time"] == "08:45"
