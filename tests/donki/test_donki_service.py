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
                        "arrivalTime": "2017-01-06T07:31Z"
                    },
                    {
                        "isGlancingBlow": True,
                        "location": "Mars",
                        "arrivalTime": "2017-01-07T06:00Z"
                    },
                    {
                        "isGlancingBlow": True,
                        "location": "STEREO A",
                        "arrivalTime": "2017-01-06T00:00Z"
                    }
                ],
                "cmeIDs": [
                    "2017-01-03T03:12:00-CME-001"
                ]
            }
        ]
    }


class TestDonkiService:

    @patch.object(BaseAPI, "get_request", return_value=json.dumps(
        [
            {
                "activityID": "2017-01-03T03:12:00-CME-001",
                "catalog": "M2M_CATALOG",
                "startTime": "2017-01-03T03:12Z",
                "instruments": [
                    {
                        "displayName": "SOHO: LASCO/C2"
                    },
                    {
                        "displayName": "SOHO: LASCO/C3"
                    }
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
                        "enlilList": None
                    }
                ],
                "linkedEvents": None
            }
        ]
    ))
    def test_donki_cme(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.cme()
        assert result

    @patch.object(BaseAPI, "get_request", return_value=json.dumps(
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
                "link": "https://webtools.ccmc.gsfc.nasa.gov/DONKI/view/CMEAnalysis/11256/-1"
            }
        ]))
    def test_donki_cme_analysis(self, get_request) -> None:
        donki_service: DonkiService = DonkiService("api_key")
        result = donki_service.cme_analyisis()
        assert result
        assert result[0].isMostAccurate
        assert not result[1].isMostAccurate
