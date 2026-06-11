from typing import List, Optional

from nasa_apis_wrapper.base import BaseAPI, NasaAPIException
from .models import ExoplanetRecord, ExoplanetTable, DiscoveryMethod


class ExoplanetService(BaseAPI):
    """
    Service for the NASA Exoplanet Archive TAP API.

    Uses the Table Access Protocol (TAP) with ADQL queries — essentially SQL
    over HTTP. No API key required.

    Two main tables:

    - ``pscomppars`` *(default)*: one row per confirmed planet, composite
      parameters drawn from the best available source for each field.
    - ``ps``: one row per planet per publication. Use ``WHERE default_flag = 1``
      to get canonical parameters, or omit it to access all measurements.

    For full column access or advanced filtering, use :meth:`query` with raw ADQL.
    """

    _ENDPOINT = "/sync"

    def __init__(self):
        super().__init__()  # Exoplanet Archive does not require an API key
        self.host = "https://exoplanetarchive.ipac.caltech.edu/TAP"

    # ------------------------------------------------------------------
    # Raw ADQL access
    # ------------------------------------------------------------------

    def query(self, adql: str) -> List[dict]:
        """
        Execute a raw ADQL query and return the results as a list of dicts.

        This gives full access to all columns and tables in the archive.

        Args:
            adql: A valid ADQL query string.
                Example: ``"SELECT pl_name, pl_masse FROM pscomppars WHERE pl_masse < 2"``

        Returns:
            List of dicts, one per row. Keys are column names, values are the
            raw Python types (str, int, float, or None).

        Raises:
            NasaAPIException: If the query fails.

        Example::

            service = ExoplanetService()
            rows = service.query(
                "SELECT TOP 10 pl_name, pl_masse, pl_rade "
                "FROM pscomppars "
                "WHERE pl_masse < 2 "
                "ORDER BY pl_masse"
            )
        """
        return self.get_request(self._ENDPOINT, params={"query": adql, "format": "json"})

    # ------------------------------------------------------------------
    # Typed methods
    # ------------------------------------------------------------------

    def planets(
        self,
        table: ExoplanetTable = "pscomppars",
        columns: Optional[List[str]] = None,
        where: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[ExoplanetRecord]:
        """
        Query planets with optional filters, returning typed records.

        Args:
            table: Archive table to query. Defaults to ``"pscomppars"``.
            columns: Columns to retrieve. If omitted, fetches all columns (``*``).
                When specifying columns, include at minimum ``pl_name`` and
                ``hostname`` as they are required by :class:`ExoplanetRecord`.
            where: ADQL ``WHERE`` clause (without the ``WHERE`` keyword).
                Example: ``"pl_masse < 2 AND tran_flag = 1"``.
            order_by: ADQL ``ORDER BY`` clause (without the keyword).
                Example: ``"pl_masse DESC"``.
            limit: Maximum number of rows to return (uses ``SELECT TOP n``).

        Returns:
            List of ExoplanetRecord objects.

        Raises:
            NasaAPIException: If the query fails.
        """
        adql = self._build_query(table, columns, where, order_by, limit)
        rows = self.query(adql)
        return [ExoplanetRecord(**row) for row in rows]

    def planet(
        self,
        name: str,
        table: ExoplanetTable = "pscomppars",
    ) -> ExoplanetRecord:
        """
        Retrieve a single planet by its exact name.

        Args:
            name: Planet name as it appears in the archive (e.g. ``"51 Peg b"``).
            table: Archive table to query. Defaults to ``"pscomppars"``.

        Returns:
            ExoplanetRecord for the requested planet.

        Raises:
            NasaAPIException: If the planet is not found or the request fails.
        """
        results = self.planets(table=table, where=f"pl_name = '{name}'")
        if not results:
            raise NasaAPIException(f"Planet '{name}' not found in table '{table}'.")
        return results[0]

    def confirmed_planets(
        self,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> List[ExoplanetRecord]:
        """
        Retrieve confirmed planets from ``pscomppars`` (one row per planet).

        This is the most common entry point for exploring the exoplanet catalogue.

        Args:
            limit: Maximum number of planets to return.
            order_by: ADQL ``ORDER BY`` clause. Example: ``"disc_year DESC"``.

        Returns:
            List of ExoplanetRecord objects, one per confirmed planet.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self.planets(table="pscomppars", order_by=order_by, limit=limit)

    def planets_by_method(
        self,
        method: DiscoveryMethod,
        limit: Optional[int] = None,
    ) -> List[ExoplanetRecord]:
        """
        Retrieve confirmed planets discovered by a specific method.

        Args:
            method: Discovery method. One of ``"Transit"``, ``"Radial Velocity"``,
                ``"Imaging"``, ``"Microlensing"``, etc.
            limit: Maximum number of results.

        Returns:
            List of ExoplanetRecord objects.

        Raises:
            NasaAPIException: If the request fails.
        """
        return self.planets(
            where=f"discoverymethod = '{method}'",
            order_by="disc_year DESC",
            limit=limit,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _build_query(
        table: str,
        columns: Optional[List[str]],
        where: Optional[str],
        order_by: Optional[str],
        limit: Optional[int],
    ) -> str:
        select = ", ".join(columns) if columns else "*"
        if limit:
            select = f"TOP {limit} {select}"
        adql = f"SELECT {select} FROM {table}"
        if where:
            adql += f" WHERE {where}"
        if order_by:
            adql += f" ORDER BY {order_by}"
        return adql
