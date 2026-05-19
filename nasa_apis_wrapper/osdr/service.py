from typing import Any, Dict, List, Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    OSDRSearchRequest,
    OSDRSearchResponse,
    OSDRFilesResponse,
    OSDRMission,
    RadLabRequest,
    RadLabMeasurement,
)


class OSDRService(BaseAPI):
    """
    Service for the NASA Open Science Data Repository (OSDR) APIs.

    Covers three sub-APIs hosted on ``osdr.nasa.gov``:

    - **OSDR Data API** — search studies and retrieve their files/metadata
    - **Geode-PY API** — relational database of missions, experiments, payloads

    No API key required.

    OSDR contains data from space biology experiments — gene expression,
    proteomics, metagenomics, and more — from missions aboard the ISS,
    Space Shuttle, and other platforms.
    """

    def __init__(self):
        super().__init__()
        self.host = "https://osdr.nasa.gov"

    # ------------------------------------------------------------------
    # OSDR Data API — Search
    # ------------------------------------------------------------------

    def search(self, request: Optional[OSDRSearchRequest] = None) -> OSDRSearchResponse:
        """
        Search OSDR studies across all data sources.

        Args:
            request: Search parameters. Use ``term`` for free-text search,
                ``type`` to restrict to a data source (``"cgene"``,
                ``"nih_geo"``, ``"ebi_pride"``, ``"mg_rast"``), and
                ``ffield``/``fvalue`` to filter by a specific metadata field.

        Returns:
            OSDRSearchResponse with Elasticsearch-style hits and total count.
            Access results via ``response.hits.hits``.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            results = service.search(OSDRSearchRequest(term="mouse", type="cgene"))
            for hit in results.hits.hits:
                print(hit.source.accession, hit.source.organism)
        """
        params = request.model_dump(by_alias=True, exclude_none=True) if request else None
        data = self.get_request("/osdr/data/search", params=params)
        return OSDRSearchResponse(**data)

    # ------------------------------------------------------------------
    # OSDR Data API — Files
    # ------------------------------------------------------------------

    def study_files(
        self,
        study_ids: str,
        page: int = 0,
        size: int = 25,
        all_files: bool = False,
    ) -> OSDRFilesResponse:
        """
        Retrieve the list of files associated with one or more studies.

        Args:
            study_ids: One or more study IDs as a string. Supports single IDs
                (``"87"``), comma-separated ranges (``"87-95,137"``), and
                versioned IDs (``"153.2"``).
            page: Page number (0-based). Defaults to 0.
            size: Results per page. Maximum 25.
            all_files: Include hidden/restricted files. Defaults to False.

        Returns:
            OSDRFilesResponse with per-study file lists. Each ``OSDRStudyFile``
            has a ``full_url`` property for direct download.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            response = service.study_files("137")
            for f in response.studies["OSD-137"].study_files:
                print(f.file_name, f.full_url)
        """
        params = {"page": page, "size": size}
        if all_files:
            params["all_files"] = "true"
        data = self.get_request(f"/osdr/data/osd/files/{study_ids}", params=params)
        return OSDRFilesResponse(**data)

    def study_metadata(self, study_id: int) -> dict:
        """
        Retrieve the full ISA (Investigation-Study-Assay) metadata for a study.

        The ISA structure is deeply nested with ontology references and varies
        significantly across studies, so the raw dict is returned. For the most
        common study information, :meth:`search` with the accession number is
        more convenient.

        Args:
            study_id: Numeric study identifier (e.g. ``137`` for OSD-137).

        Returns:
            Raw dict with the full ISA metadata structure.

        Raises:
            NasaAPIException: If the study is not found.
        """
        return self.get_request(f"/osdr/data/osd/meta/{study_id}")

    # ------------------------------------------------------------------
    # Geode-PY API — Missions
    # ------------------------------------------------------------------

    def missions(self) -> List[str]:
        """
        List all mission identifiers in the OSDR relational database.

        Returns:
            List of mission identifier strings (e.g. ``["STS-135", "SpaceX-4", ...]``).

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request("/geode-py/ws/api/missions/")
        return [item["mission"].rstrip("/").split("/")[-1] for item in data["data"]]

    def mission(self, identifier: str) -> OSDRMission:
        """
        Retrieve details for a specific mission.

        Args:
            identifier: Mission identifier (e.g. ``"STS-135"``, ``"SpaceX-4"``).
                Use :meth:`missions` to list all available identifiers.

        Returns:
            OSDRMission with dates and aliases.

        Raises:
            NasaAPIException: If the mission is not found.
        """
        data = self.get_request(f"/geode-py/ws/api/mission/{identifier}")
        return OSDRMission(**data)

    def experiments(self) -> List[str]:
        """
        List all experiment identifiers in the OSDR relational database.

        Returns:
            List of experiment identifier strings.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request("/geode-py/ws/api/experiments/")
        return [item["experiment"].rstrip("/").split("/")[-1] for item in data["data"]]

    def experiment(self, identifier: str) -> dict:
        """
        Retrieve full details for a specific experiment.

        The experiment structure is complex (people, payloads, missions,
        protocol, files) so the raw dict is returned.

        Args:
            identifier: Experiment identifier string.

        Returns:
            Raw dict with the full experiment record.

        Raises:
            NasaAPIException: If the experiment is not found.
        """
        return self.get_request(f"/geode-py/ws/api/experiment/{identifier}")


class RadLabService(BaseAPI):
    """
    Service for the OSDR RadLab radiation measurement API.

    Provides access to in-situ radiation measurements from instruments aboard
    spacecraft including the ISS, Matroshka phantom, and satellites. Data
    includes absorbed dose rate, dose equivalent rate, particle flux, and
    orbital parameters. No API key required.

    Example instruments:
        - DOSTEL (ISS Columbus)
        - TEPC (ISS)
        - STS Shuttle detectors
        - MATROSHKA phantom detectors
    """

    def __init__(self):
        super().__init__()
        self.host = "https://visualization.osdr.nasa.gov"

    def measurements(
        self, request: Optional[RadLabRequest] = None
    ) -> List[RadLabMeasurement]:
        """
        Query radiation measurements with optional filters.

        All filter fields in ``request`` are optional and combinable. Date
        comparisons use ISO 8601 strings.

        Args:
            request: Query filters. Use ``spacecraft``, ``timestamp_gte``/
                ``timestamp_lte`` for time ranges, and ``absorbed_dose_rate_gte``
                for threshold filtering.

        Returns:
            List of RadLabMeasurement objects. Can be empty if no records
            match the filters.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            data = service.measurements(RadLabRequest(
                spacecraft="ISS",
                timestamp_gte="2020-01-01T00:00:00Z",
                timestamp_lte="2020-01-02T00:00:00Z",
            ))
            for m in data:
                print(m.timestamp, m.absorbed_dose_rate, m.altitude)
        """
        params = {"format": "json"}
        if request:
            params.update(request.model_dump(by_alias=True, exclude_none=True))
            params.pop("format", None)
            params["format"] = "json"
        rows = self.get_request("/radlab/api", params=params)
        return [RadLabMeasurement(**row) for row in rows]


class BioDataService(BaseAPI):
    """
    Service for the OSDR Biological Data API v2.

    Provides access to space biology datasets (RNA-seq, proteomics, metagenomics)
    through two complementary interfaces:

    - **REST interface** — navigate the dataset/assay/sample/file hierarchy
      with structured methods.
    - **Query interface** — filter across all samples or assays using field-level
      predicates. Supports exact match, OR (``|``), NOT (``!=``), and regex
      (``/pattern/i``).

    No API key required. Wildcards (``"*"``) are accepted in place of any
    accession, assay, or sample name to target all entities at that level.

    Example field filters (passed as ``**kwargs``)::

        organism="Mus musculus"
        organism="Mus musculus|Homo sapiens"          # OR
        organism!="Arabidopsis thaliana"              # NOT
        organism="/^Mus/i"                            # regex, case-insensitive
        **{"study.factor_value.spaceflight": "Flight"}  # dot-notation field
    """

    _BASE = "/biodata/api/v2"

    def __init__(self):
        super().__init__()
        self.host = "https://visualization.osdr.nasa.gov"

    # ------------------------------------------------------------------
    # REST interface — dataset / assay / sample hierarchy
    # ------------------------------------------------------------------

    def datasets(self) -> Dict[str, str]:
        """
        List all available dataset accessions and their REST URLs.

        Returns:
            Dict mapping accession (e.g. ``"OSD-1"``) to its REST URL.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request(f"{self._BASE}/datasets/", params={"format": "json"})
        return {acc: entry["REST_URL"] for acc, entry in data.items()}

    def dataset(self, accession: str) -> dict:
        """
        Retrieve metadata for a single dataset.

        Args:
            accession: Dataset accession (e.g. ``"OSD-48"``).

        Returns:
            Raw dict with study title, organism, mission, assay links, and more.

        Raises:
            NasaAPIException: If the dataset is not found.
        """
        return self.get_request(f"{self._BASE}/dataset/{accession}/", params={"format": "json"})

    def assays(self, accession: str) -> List[str]:
        """
        List assay names for a dataset.

        Args:
            accession: Dataset accession (e.g. ``"OSD-48"``).

        Returns:
            List of assay name strings (e.g.
            ``["OSD-48_transcription_profiling_RNA_Sequencing_Illumina"]``).

        Raises:
            NasaAPIException: If the dataset is not found.
        """
        data = self.get_request(
            f"{self._BASE}/dataset/{accession}/assays/",
            params={"format": "json"},
        )
        return list(data[accession]["assays"].keys())

    def samples(self, accession: str, assay_name: str) -> List[str]:
        """
        List sample names for a given assay.

        Args:
            accession: Dataset accession.
            assay_name: Assay name as returned by :meth:`assays`.

        Returns:
            List of sample name strings.

        Raises:
            NasaAPIException: If the assay is not found.
        """
        data = self.get_request(
            f"{self._BASE}/dataset/{accession}/assay/{assay_name}/samples/",
            params={"format": "json"},
        )
        return list(data[accession]["assays"][assay_name]["samples"].keys())

    def sample(self, accession: str, assay_name: str, sample_name: str) -> dict:
        """
        Retrieve the combined ISA record for a single sample.

        The response merges investigation, study, and assay sections following
        the ISA-Tab specification.

        Args:
            accession: Dataset accession.
            assay_name: Assay name.
            sample_name: Sample name.

        Returns:
            Dict with ``"investigation"``, ``"study"``, ``"assay"``, and
            ``"files_url"`` keys.

        Raises:
            NasaAPIException: If the sample is not found.
        """
        return self.get_request(
            f"{self._BASE}/dataset/{accession}/assay/{assay_name}/sample/{sample_name}/",
            params={"format": "json"},
        )

    def files(
        self,
        accession: str,
        assay_name: Optional[str] = None,
        sample_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List files at dataset, assay, or sample level.

        Args:
            accession: Dataset accession.
            assay_name: If provided, scopes to this assay.
            sample_name: If provided (requires ``assay_name``), scopes to
                this sample.

        Returns:
            Dict mapping filename to its metadata (``"REST_URL"`` and ``"URL"``).

        Raises:
            NasaAPIException: If the resource is not found.
        """
        if sample_name and assay_name:
            path = f"{self._BASE}/dataset/{accession}/assay/{assay_name}/sample/{sample_name}/files/"
        elif assay_name:
            path = f"{self._BASE}/dataset/{accession}/assay/{assay_name}/files/"
        else:
            path = f"{self._BASE}/dataset/{accession}/files/"
        return self.get_request(path, params={"format": "json"})

    # ------------------------------------------------------------------
    # Query interface — cross-dataset filtering
    # ------------------------------------------------------------------

    def query_samples(self, **filters: str) -> List[Dict[str, Any]]:
        """
        Query sample-level metadata across all datasets.

        Each keyword argument is sent as a query parameter. Field names follow
        dot-notation (e.g. ``study.factor_value.spaceflight``). Values support
        the API's filter operators:

        - Exact: ``organism="Mus musculus"``
        - OR: ``organism="Mus musculus|Homo sapiens"``
        - NOT: pass the key as ``organism!=value`` via ``**{"organism!=": "..."}``
        - Regex: ``organism="/^Mus/i"``

        Args:
            **filters: Field-value pairs used as query parameters.

        Returns:
            List of dicts, one per sample, with all requested metadata fields.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            rows = service.query_samples(organism="Mus musculus")
            for row in rows:
                print(row["id.accession"], row["id.sample_name"])
        """
        params = {"format": "json.records", **filters}
        return self.get_request(f"{self._BASE}/query/metadata/", params=params)

    def query_assays(self, **filters: str) -> List[Dict[str, Any]]:
        """
        Query assay-level metadata (one row per assay, deduplicated).

        Accepts the same filter syntax as :meth:`query_samples`.

        Args:
            **filters: Field-value pairs used as query parameters.

        Returns:
            List of dicts, one per assay.

        Raises:
            NasaAPIException: If the request fails.
        """
        params = {"format": "json.records", **filters}
        return self.get_request(f"{self._BASE}/query/assays/", params=params)

    def query_data(self, **filters: str) -> List[Dict[str, Any]]:
        """
        Query raw tabular data (e.g. RNA-seq counts, differential expression).

        Requires ``file.data_type`` and usually ``file.file_name`` filters to
        scope the query to a specific data file.

        Args:
            **filters: Field-value pairs. Use ``file.data_type`` to select the
                data type (e.g. ``"unnormalized_counts"``,
                ``"differential_expression"``).

        Returns:
            List of dicts with the tabular data rows.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            rows = service.query_data(**{
                "id.accession": "OSD-48",
                "file.data_type": "unnormalized_counts",
            })
        """
        params = {"format": "json.records", **filters}
        return self.get_request(f"{self._BASE}/query/data/", params=params)
