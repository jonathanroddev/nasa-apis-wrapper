import json
from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, DonkiService


def generate_cme_analysis_item() -> dict:
    return {
        "isMostAccurate": True,
        "time21_5": "2017-01-03T13:08Z",
        "latitude": -10.0,
        "longitude": -105.0,
        "halfAngle": 20.0,
        "speed": 645.0,
        "type": "C",
        "featureCode": "null",
        "imageType": None,
        "measurementTechnique": "null",
        "note": "Measured using SOHO LASCO C3 imagery.",
        "levelOfData": 0,
        "tilt": None,
        "minorHalfWidth": None,
        "speedMeasuredAtHeight": None,
        "submissionTime": "2017-01-03T18:49Z",
        "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/CMEAnalysis/12059/-1",
        "enlilList": [
            {
                "modelCompletionTime": "2017-01-03T21:57Z",
                "au": 2.0,
                "estimatedShockArrivalTime": None,
                "estimatedDuration": None,
                "rmin_re": None,
                "kp_18": None,
                "kp_90": None,
                "kp_135": None,
                "kp_180": None,
                "isEarthGB": False,
                "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/WSA-ENLIL/12061/-1",
                "impactList": [
                    {
                        "isGlancingBlow": False,
                        "location": "Spitzer",
                        "arrivalTime": "2017-01-06T07:31Z",
                    }
                ],
                "cmeIDs": ["2017-01-03T03:12:00-CME-001"],
            }
        ],
    }


class TestDonkiService:

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "activityID": "2017-01-03T03:12:00-CME-001",
                    "catalog": "M2M_CATALOG",
                    "startTime": "2017-01-03T03:12Z",
                    "instruments": [
                        {"displayName": "SOHO: LASCO/C2"},
                        {"displayName": "SOHO: LASCO/C3"},
                    ],
                    "sourceLocation": "",
                    "activeRegionNum": None,
                    "note": "The CME has two stages, the first starting at 03:12Z and the second at 06:00Z. The second stage merges with the first stage and that is what is measured. The source is a small off limb eruption in the SE of SDO AIA 171 between 01:55Z and 02:43Z.",
                    "submissionTime": "2017-01-03T19:40Z",
                    "versionId": 2,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/CME/12056/-1",
                    "cmeAnalyses": [
                        generate_cme_analysis_item(),
                        {
                            "isMostAccurate": False,
                            "time21_5": "2017-01-03T18:39Z",
                            "latitude": -12.0,
                            "longitude": -110.0,
                            "halfAngle": 13.0,
                            "speed": 270.0,
                            "type": "S",
                            "featureCode": "null",
                            "imageType": None,
                            "measurementTechnique": "null",
                            "note": "",
                            "levelOfData": 0,
                            "tilt": None,
                            "minorHalfWidth": None,
                            "speedMeasuredAtHeight": None,
                            "submissionTime": "2017-01-03T12:34Z",
                            "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/CMEAnalysis/12057/-1",
                            "enlilList": None,
                        },
                    ],
                    "linkedEvents": None,
                }
            ]
        ),
    )
    def test_donki_cme(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.cme()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                generate_cme_analysis_item(),
                {
                    "time21_5": "2016-09-15T04:24Z",
                    "latitude": -18.0,
                    "longitude": -122.0,
                    "halfAngle": 43.0,
                    "speed": 722.0,
                    "type": "C",
                    "isMostAccurate": False,
                    "associatedCMEID": "2016-09-14T23:36:00-CME-001",
                    "note": "Measured with swpc_cat using C3 and STA Cor2 imagery.",
                    "catalog": "M2M_CATALOG",
                    "featureCode": "null",
                    "dataLevel": "1",
                    "measurementTechnique": "null",
                    "imageType": "null",
                    "tilt": None,
                    "minorHalfWidth": None,
                    "speedMeasuredAtHeight": None,
                    "submissionTime": "2016-09-15T13:22Z",
                    "versionId": 1,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/CMEAnalysis/11256/-1",
                },
            ]
        ),
    )
    def test_donki_cme_analysis(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.cme_analyisis()
        assert result
        assert result[0].isMostAccurate
        assert not result[1].isMostAccurate

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "gstID": "2016-01-21T03:00:00-GST-001",
                    "startTime": "2016-01-21T03:00Z",
                    "allKpIndex": [
                        {
                            "observedTime": "2016-01-21T06:00Z",
                            "kpIndex": 6.0,
                            "source": "NOAA",
                        }
                    ],
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/GST/10074/-1",
                    "linkedEvents": [
                        {"activityID": "2016-01-15T00:00:00-CME-001"},
                    ],
                    "submissionTime": "2016-01-21T06:28Z",
                    "versionId": 1,
                }
            ]
        ),
    )
    def test_donki_gst(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.gst()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "catalog": "M2M_CATALOG",
                    "activityID": "2016-01-09T18:00:00-IPS-001",
                    "location": "STEREO A",
                    "eventTime": "2016-01-09T18:00Z",
                    "submissionTime": "2016-01-11T21:18Z",
                    "versionId": 2,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/IPS/10028/-1",
                    "instruments": [
                        {"displayName": "STEREO A: IMPACT"},
                    ],
                }
            ]
        ),
    )
    def test_donki_ips(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.ips()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "flrID": "2016-01-01T23:00:00-FLR-001",
                    "catalog": "M2M_CATALOG",
                    "instruments": [{"displayName": "GOES15: SEM/XRS 1.0-8.0"}],
                    "beginTime": "2016-01-01T23:00Z",
                    "peakTime": "2015-01-02T00:10Z",
                    "endTime": None,
                    "classType": "M2.3",
                    "sourceLocation": "S21W73",
                    "activeRegionNum": 12473,
                    "note": "Associated eruption visible in SOD AIA 171. 193, and 304 with opening field lines and filament liftoff.",
                    "submissionTime": "2016-01-04T09:22Z",
                    "versionId": 2,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/FLR/9963/-1",
                    "linkedEvents": [
                        {"activityID": "2016-01-01T23:12:00-CME-001"},
                    ],
                }
            ]
        ),
    )
    def test_donki_flr(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.flr()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "sepID": "2016-01-02T02:48:00-SEP-001",
                    "eventTime": "2016-01-02T02:48Z",
                    "instruments": [{"displayName": "SOHO: COSTEP 15.8-39.8 MeV"}],
                    "submissionTime": "2016-01-02T04:45Z",
                    "versionId": 1,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/SEP/9966/-1",
                    "linkedEvents": [
                        {"activityID": "2016-01-01T23:00:00-FLR-001"},
                    ],
                }
            ]
        ),
    )
    def test_donki_sep(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.sep()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "mpcID": "2016-03-06T16:32:00-MPC-001",
                    "eventTime": "2016-03-06T16:32Z",
                    "instruments": [{"displayName": "MODEL: SWMF"}],
                    "submissionTime": "2016-03-06T16:26Z",
                    "versionId": 1,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/MPC/10300/-1",
                    "linkedEvents": [{"activityID": "2016-03-06T04:30:00-IPS-001"}],
                }
            ]
        ),
    )
    def test_donki_mpc(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.mpc()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "rbeID": "2016-01-02T12:25:00-RBE-001",
                    "eventTime": "2016-01-02T12:25Z",
                    "instruments": [{"displayName": "GOES13: SEM/EPS \u003e0.8 MeV"}],
                    "submissionTime": "2016-01-02T13:25Z",
                    "versionId": 2,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/RBE/9969/-1",
                    "linkedEvents": [{"activityID": "2015-12-28T12:39:00-CME-001"}],
                }
            ]
        ),
    )
    def test_donki_rbe(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.rbe()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "hssID": "2025-05-27T18:55:00-HSS-001",
                    "eventTime": "2025-05-27T18:55Z",
                    "instruments": [{"displayName": "DSCOVR: PLASMAG"}],
                    "submissionTime": "2025-05-28T11:16Z",
                    "versionId": 1,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/HSS/39130/-1",
                    "linkedEvents": None,
                }
            ]
        ),
    )
    def test_donki_hss(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.hss()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "simulationID": "WSA-ENLIL/1328/1",
                    "modelCompletionTime": "2011-09-19T08:54Z",
                    "au": 2,
                    "cmeInputs": [
                        {
                            "cmeStartTime": "2011-09-19T02:09Z",
                            "latitude": 21,
                            "longitude": -126,
                            "speed": 355,
                            "halfAngle": 40,
                            "time21_5": "2011-09-19T09:38Z",
                            "featureCode": "null",
                            "isMostAccurate": True,
                            "levelOfData": 0,
                            "ipsList": [],
                            "cmeid": "2011-09-19T02:09:00-CME-001",
                        }
                    ],
                    "estimatedShockArrivalTime": None,
                    "estimatedDuration": None,
                    "rmin_re": None,
                    "kp_18": None,
                    "kp_90": None,
                    "kp_135": None,
                    "kp_180": None,
                    "isEarthGB": False,
                    "impactList": None,
                    "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/WSA-ENLIL/1328/-1",
                }
            ]
        ),
    )
    def test_donki_wsa_enlis_simulation(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.wsa_enlil_simulation()
        assert result

    @patch.object(
        BaseAPI,
        "get_request",
        return_value=json.dumps(
            [
                {
                    "messageType": "FLR",
                    "messageID": "20140508-AL-002",
                    "messageURL": "https://kauai.ccmc.gsfc.nasa.gov/DONKI/view/Alert/5432/1",
                    "messageIssueTime": "2014-05-08T12:43Z",
                    "messageBody": "## NASA Goddard Space Flight Center, Space Weather Research Center ( SWRC )\n## Message Type: Space Weather Notification",
                }
            ]
        ),
    )
    def test_donki_notifications(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.notifications()
        assert result
