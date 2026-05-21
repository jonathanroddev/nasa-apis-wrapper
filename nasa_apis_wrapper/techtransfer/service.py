from typing import Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    PatentResponse,
    SoftwareResponse,
    SpinoffResponse,
    TechTransferSearchResponse,
)


class TechTransferService(BaseAPI):
    """
    Service for the NASA TechTransfer API.

    TechTransfer exposes NASA's portfolio of patents, software releases, and
    spinoff products — commercial technologies derived from NASA R&D. All
    endpoints accept a free-text search query.

    Results are returned as typed Pydantic models parsed from the API's
    columnar format (list-of-lists). ``description`` and ``abstract`` fields
    contain HTML markup.

    An API key is recommended but the DEMO_KEY rate limits apply if none is
    provided.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.host = "https://technology.nasa.gov/api"

    def patents(self, query: str) -> PatentResponse:
        """
        Search NASA patents by keyword.

        Args:
            query: Free-text search term (e.g., ``"solar"``).

        Returns:
            PatentResponse with a paginated list of ``PatentResult`` objects.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.patents("solar sail")
            for patent in result.results:
                print(patent.case_number, patent.title, patent.center)
        """
        data = self.get_request("/patent", params={"patent": query})
        return PatentResponse(**data)

    def software(self, query: str) -> SoftwareResponse:
        """
        Search NASA software releases by keyword.

        NASA software can be released as Open Source or under Government
        Purpose Rights (GPR), depending on the classification.

        Args:
            query: Free-text search term (e.g., ``"trajectory"``).

        Returns:
            SoftwareResponse with a paginated list of ``SoftwareResult`` objects.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.software("propulsion")
            for sw in result.results:
                print(sw.case_number, sw.title, sw.release_type)
        """
        data = self.get_request("/software", params={"software": query})
        return SoftwareResponse(**data)

    def spinoffs(self, query: str) -> SpinoffResponse:
        """
        Search NASA spinoff products by keyword.

        Spinoffs are commercial products and services developed with NASA
        technology, published annually in the NASA Spinoff magazine since 1976.

        Args:
            query: Free-text search term (e.g., ``"medical"``).

        Returns:
            SpinoffResponse with a paginated list of ``SpinoffResult`` objects.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.spinoffs("water purification")
            for spinoff in result.results:
                print(spinoff.title, spinoff.year, spinoff.company)
        """
        data = self.get_request("/spinoff", params={"spinoff": query})
        return SpinoffResponse(**data)

    def search(self, query: str) -> TechTransferSearchResponse:
        """
        Search across all technology types (patents, software, spinoffs).

        Args:
            query: Free-text search term.

        Returns:
            TechTransferSearchResponse with mixed ``TechTransferItem`` records.
            Each item has a ``type`` field indicating its category.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.search("rover")
            for item in result.results:
                print(item.type, item.title)
        """
        data = self.get_request("/techtransfer", params={"techtransfer": query})
        return TechTransferSearchResponse(**data)
