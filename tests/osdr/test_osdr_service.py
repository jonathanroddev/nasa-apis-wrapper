from unittest.mock import patch

from nasa_apis_wrapper import BaseAPI, OSDRService, RadLabService, BioDataService
from nasa_apis_wrapper import OSDRSearchRequest, RadLabRequest

SEARCH_RESPONSE = {
    "took": 12,
    "timed_out": False,
    "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
    "hits": {
        "total": 247,
        "max_score": 8.5,
        "hits": [
            {
                "_index": "study",
                "_type": "docs",
                "_id": "OSD-48",
                "_score": 8.5,
                "_source": {
                    "Accession": "OSD-48",
                    "Study Title": "Effects of spaceflight on murine skeletal muscle",
                    "Study Description": "Mouse muscle tissue from ISS mission.",
                    "organism": "Mus musculus",
                    "Project Type": "Spaceflight Study",
                    "Experiment Platform": "International Space Station (ISS)",
                    "Space Program": "NASA",
                    "Managing NASA Center": "Ames Research Center (ARC)",
                    "Study Public Release Date": 1412121600.0,
                    "thumbnail": "/geode-py/ws/studies/OSD-48/image",
                    "Mission": {
                        "Name": "SpaceX-4",
                        "Start Date": "9/21/14",
                        "End Date": "10/25/2014",
                    },
                    "Study Person": {
                        "First Name": "Ruth",
                        "Middle Initials": "E",
                        "Last Name": "Globus",
                    },
                    "Flight Program": "ISS National Lab",
                    "Factor Value": "spaceflight",
                    "links": [],
                },
            }
        ],
    },
}

FILES_RESPONSE = {
    "hits": 1,
    "input": "137",
    "page_number": 1,
    "page_size": 25,
    "page_total": 1,
    "success": True,
    "total_hits": 1,
    "valid_input": ["OSD-137"],
    "studies": {
        "OSD-137": {
            "file_count": 2,
            "study_files": [
                {
                    "category": "RNA-Seq Alignment",
                    "date_created": 1609459200.0,
                    "date_updated": 1612137600.0,
                    "file_name": "GLDS-137_rna_seq_alignment.tgz",
                    "file_size": 524288000,
                    "organization": "genelab",
                    "remote_url": "/genelab/static/media/dataset/GLDS-137_rna_seq.tgz",
                    "restricted": False,
                    "subcategory": "",
                    "subdirectory": "",
                    "visible": True,
                },
                {
                    "category": "Metadata",
                    "date_created": 1609459200.0,
                    "date_updated": "",
                    "file_name": "s_GLDS-137.txt",
                    "file_size": 4096,
                    "organization": "OSD",
                    "remote_url": "/osdr/bio/repo/data/studies/GeneLab/OSD-137/metadata/s_GLDS-137.txt",
                    "restricted": False,
                    "subcategory": "",
                    "subdirectory": "metadata",
                    "visible": True,
                },
            ],
        }
    },
}

MISSIONS_RESPONSE = {
    "data": [
        {"mission": "https://osdr.nasa.gov/geode-py/ws/api/mission/STS-135"},
        {"mission": "https://osdr.nasa.gov/geode-py/ws/api/mission/SpaceX-4"},
    ]
}

MISSION_RESPONSE = {
    "id": "42",
    "identifier": "STS-135",
    "identifierLowercase": "sts-135",
    "esID": "sts-135",
    "aliases": ["Atlantis STS-135"],
    "startDate": "2011-07-08",
    "endDate": "2011-07-21",
    "versionInfo": {"documentKey": "abc", "version": 1, "deleted": False},
    "files": [],
    "vehicle": {"vehicle": "https://osdr.nasa.gov/geode-py/ws/api/vehicle/Atlantis"},
    "people": [],
    "parents": {},
}

RADLAB_RESPONSE = [
    {
        "celestial_body": "Earth",
        "trajectory": "ISS",
        "spacecraft": "ISS",
        "module": "Columbus",
        "instrument_family": "DOSTEL",
        "instrument": "DOSTEL-1",
        "instrument_id": "DOSTEL1_Columbus",
        "timestamp": "2020-01-01T00:00:00Z",
        "absorbed_dose_rate": 5.42,
        "dose_equivalent_rate": 12.3,
        "flux": None,
        "latitude": 51.6,
        "longitude": -122.4,
        "altitude": 408.0,
        "B": None,
        "L": None,
    }
]


class TestOSDRService:

    def test_no_api_key_required(self) -> None:
        service = OSDRService()
        assert service.host == "https://osdr.nasa.gov"
        assert "api_key" not in (service.session.params or {})

    @patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE)
    def test_search_returns_response(self, _) -> None:
        result = OSDRService().search(OSDRSearchRequest(term="mouse"))
        assert result.hits.total == 247
        assert len(result.hits.hits) == 1

    @patch.object(BaseAPI, "get_request", return_value=SEARCH_RESPONSE)
    def test_search_hit_source(self, _) -> None:
        hit = OSDRService().search().hits.hits[0]
        assert hit.id == "OSD-48"
        assert hit.source.accession == "OSD-48"
        assert hit.source.organism == "Mus musculus"
        assert hit.source.mission.name == "SpaceX-4"
        assert hit.source.study_person.last_name == "Globus"

    @patch.object(BaseAPI, "get_request", return_value=FILES_RESPONSE)
    def test_study_files(self, _) -> None:
        result = OSDRService().study_files("137")
        study = result.studies["OSD-137"]
        assert study.file_count == 2
        assert study.study_files[0].file_name == "GLDS-137_rna_seq_alignment.tgz"
        assert study.study_files[0].full_url.startswith("https://osdr.nasa.gov")

    @patch.object(BaseAPI, "get_request", return_value=FILES_RESPONSE)
    def test_study_file_date_updated_can_be_empty_string(self, _) -> None:
        files = OSDRService().study_files("137").studies["OSD-137"].study_files
        assert files[1].date_updated == ""

    @patch.object(BaseAPI, "get_request", return_value=MISSIONS_RESPONSE)
    def test_missions_list(self, _) -> None:
        result = OSDRService().missions()
        assert result == ["STS-135", "SpaceX-4"]

    @patch.object(BaseAPI, "get_request", return_value=MISSION_RESPONSE)
    def test_mission_detail(self, _) -> None:
        result = OSDRService().mission("STS-135")
        assert result.identifier == "STS-135"
        assert result.startDate == "2011-07-08"
        assert result.aliases == ["Atlantis STS-135"]


ASSAY_NAME = "OSD-48_transcription_profiling_RNA_Sequencing_Illumina"

DATASETS_RESPONSE = {
    "OSD-1": {"REST_URL": "https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-1/"},
    "OSD-48": {"REST_URL": "https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-48/"},
}

ASSAYS_RESPONSE = {
    "OSD-48": {
        "assays": {
            ASSAY_NAME: {"REST_URL": f"https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-48/assay/{ASSAY_NAME}/"},
        }
    }
}

SAMPLES_RESPONSE = {
    "OSD-48": {
        "assays": {
            ASSAY_NAME: {
                "samples": {
                    "FLT_Rep1_C57BL6J": {"REST_URL": "..."},
                    "GC_Rep1_C57BL6J": {"REST_URL": "..."},
                }
            }
        }
    }
}

QUERY_RECORDS = [
    {"id.accession": "OSD-48", "id.assay_name": ASSAY_NAME, "id.sample_name": "FLT_Rep1_C57BL6J", "organism": "Mus musculus"},
    {"id.accession": "OSD-48", "id.assay_name": ASSAY_NAME, "id.sample_name": "GC_Rep1_C57BL6J", "organism": "Mus musculus"},
]


class TestBioDataService:

    def test_no_api_key_required(self) -> None:
        service = BioDataService()
        assert service.host == "https://visualization.osdr.nasa.gov"
        assert "api_key" not in (service.session.params or {})

    @patch.object(BaseAPI, "get_request", return_value=DATASETS_RESPONSE)
    def test_datasets(self, _) -> None:
        result = BioDataService().datasets()
        assert "OSD-48" in result
        assert result["OSD-48"].startswith("https://")

    @patch.object(BaseAPI, "get_request", return_value=ASSAYS_RESPONSE)
    def test_assays(self, _) -> None:
        result = BioDataService().assays("OSD-48")
        assert result == [ASSAY_NAME]

    @patch.object(BaseAPI, "get_request", return_value=SAMPLES_RESPONSE)
    def test_samples(self, _) -> None:
        result = BioDataService().samples("OSD-48", ASSAY_NAME)
        assert "FLT_Rep1_C57BL6J" in result
        assert "GC_Rep1_C57BL6J" in result

    @patch.object(BaseAPI, "get_request", return_value=QUERY_RECORDS)
    def test_query_samples(self, _) -> None:
        rows = BioDataService().query_samples(organism="Mus musculus")
        assert len(rows) == 2
        assert rows[0]["id.accession"] == "OSD-48"
        assert rows[0]["organism"] == "Mus musculus"

    @patch.object(BaseAPI, "get_request", return_value=QUERY_RECORDS)
    def test_query_assays(self, _) -> None:
        rows = BioDataService().query_assays(**{"id.accession": "OSD-48"})
        assert len(rows) == 2

    @patch.object(BaseAPI, "get_request", return_value=QUERY_RECORDS)
    def test_query_data(self, _) -> None:
        rows = BioDataService().query_data(**{
            "id.accession": "OSD-48",
            "file.data_type": "unnormalized_counts",
        })
        assert isinstance(rows, list)


class TestRadLabService:

    def test_no_api_key_required(self) -> None:
        service = RadLabService()
        assert service.host == "https://visualization.osdr.nasa.gov"
        assert "api_key" not in (service.session.params or {})

    @patch.object(BaseAPI, "get_request", return_value=RADLAB_RESPONSE)
    def test_measurements(self, _) -> None:
        result = RadLabService().measurements(RadLabRequest(spacecraft="ISS"))
        assert len(result) == 1
        assert result[0].spacecraft == "ISS"
        assert result[0].absorbed_dose_rate == 5.42
        assert result[0].flux is None
        assert result[0].altitude == 408.0

    @patch.object(BaseAPI, "get_request", return_value=RADLAB_RESPONSE)
    def test_measurements_no_request(self, _) -> None:
        result = RadLabService().measurements()
        assert isinstance(result, list)
