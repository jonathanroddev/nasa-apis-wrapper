from typing import Optional

from nasa_apis_wrapper.base import BaseAPI
from .models import (
    MarsRover,
    MarsRoverLatestPhotosResponse,
    MarsRoverPhotosResponse,
    RoverManifest,
    RoverManifestResponse,
    RoversResponse,
)


class MarsRoverService(BaseAPI):
    """
    Service for the NASA Mars Rover Photos API.

    Provides access to imagery captured by NASA's Mars surface rovers:

    - **Curiosity** (active since Aug 2012, Gale Crater)
    - **Opportunity** (2004–2018, Meridiani Planum)
    - **Spirit** (2004–2010, Gusev Crater)
    - **Perseverance** (active since Feb 2021, Jezero Crater)

    Each rover carries multiple cameras. Common camera codes:

    +----------+----------------------------------------+---------------------------+
    | Code     | Full name                              | Rovers                    |
    +==========+========================================+===========================+
    | FHAZ     | Front Hazard Avoidance Camera          | All                       |
    | RHAZ     | Rear Hazard Avoidance Camera           | All                       |
    | NAVCAM   | Navigation Camera                      | All                       |
    | MAST     | Mast Camera                            | Curiosity                 |
    | CHEMCAM  | Chemistry and Camera Complex           | Curiosity                 |
    | MAHLI    | Mars Hand Lens Imager                  | Curiosity                 |
    | MARDI    | Mars Descent Imager                    | Curiosity                 |
    | PANCAM   | Panoramic Camera                       | Opportunity, Spirit       |
    | MINITES  | Miniature Thermal Emission Spectrometer| Opportunity, Spirit       |
    | ENTRY    | Entry Descent Landing Camera           | Perseverance              |
    | MCZ_LEFT | Mastcam-Z Left                         | Perseverance              |
    | MCZ_RIGHT| Mastcam-Z Right                        | Perseverance              |
    | WATSON   | SHERLOC WATSON Camera                  | Perseverance              |
    +----------+----------------------------------------+---------------------------+

    Requires an API key.
    """

    _PREFIX = "/mars-photos/api/v1/rovers"
    _MANIFESTS = "/mars-photos/api/v1/manifests"

    def rovers(self) -> RoversResponse:
        """
        List all Mars rovers and their mission summary.

        Returns:
            RoversResponse with a ``rovers`` list of :class:`RoverSummary`,
            each containing mission dates, status, total photo count, and
            available camera list.

        Raises:
            NasaAPIException: If the request fails.
        """
        data = self.get_request(self._PREFIX)
        return RoversResponse(**data)

    def rover(self, rover: MarsRover) -> RoverManifest:
        """
        Retrieve the full mission manifest for a single rover.

        The manifest includes a per-sol breakdown (``photos``) listing the
        Earth date, total photos, and active cameras for every sol that has
        imagery available.

        Args:
            rover: Rover name — ``"curiosity"``, ``"opportunity"``,
                ``"spirit"``, or ``"perseverance"``.

        Returns:
            RoverManifest with mission metadata and the full ``photos``
            sol list.

        Raises:
            NasaAPIException: If the rover name is invalid or the request fails.

        Example::

            manifest = svc.rover("curiosity")
            print(manifest.max_sol, manifest.total_photos)
            print(manifest.photos[-1].cameras)
        """
        data = self.get_request(f"{self._MANIFESTS}/{rover}")
        return RoverManifestResponse(**data).photo_manifest

    def photos(
        self,
        rover: MarsRover,
        sol: Optional[int] = None,
        earth_date: Optional[str] = None,
        camera: Optional[str] = None,
        page: Optional[int] = None,
    ) -> MarsRoverPhotosResponse:
        """
        Retrieve photos taken by a rover on a specific sol or Earth date.

        Either ``sol`` or ``earth_date`` must be provided (not both).

        Args:
            rover: Rover name.
            sol: Martian solar day (0-based from landing). Use :meth:`rover`
                to find the ``max_sol`` for the latest available imagery.
            earth_date: Earth date in ``"YYYY-MM-DD"`` format. Alternative
                to ``sol``.
            camera: Camera short code to filter by (e.g. ``"NAVCAM"``,
                ``"MAST"``). If omitted, all cameras are returned.
            page: Page number for pagination (25 photos per page by default).

        Returns:
            MarsRoverPhotosResponse with a ``photos`` list of
            :class:`MarsRoverPhoto`. Each photo has ``img_src`` (the full-size
            JPEG URL), ``sol``, ``earth_date``, ``camera``, and ``rover``.

        Raises:
            NasaAPIException: If the request fails.
            ValueError: If neither ``sol`` nor ``earth_date`` is provided.

        Example::

            resp = svc.photos("curiosity", sol=1000, camera="NAVCAM")
            for photo in resp.photos:
                print(photo.img_src)
        """
        if sol is None and earth_date is None:
            raise ValueError("Either 'sol' or 'earth_date' must be provided.")
        params: dict = {}
        if sol is not None:
            params["sol"] = sol
        if earth_date is not None:
            params["earth_date"] = earth_date
        if camera is not None:
            params["camera"] = camera.lower()
        if page is not None:
            params["page"] = page
        data = self.get_request(f"{self._PREFIX}/{rover}/photos", params=params)
        return MarsRoverPhotosResponse(**data)

    def latest_photos(
        self,
        rover: MarsRover,
        camera: Optional[str] = None,
    ) -> MarsRoverLatestPhotosResponse:
        """
        Retrieve the most recently transmitted photos from a rover.

        Returns photos from the latest sol for which the rover sent back data.
        For active rovers (Curiosity, Perseverance) this is within the last
        few sols; for inactive rovers it reflects the final downlink.

        Args:
            rover: Rover name.
            camera: Optional camera filter (short code, e.g. ``"FHAZ"``).

        Returns:
            MarsRoverLatestPhotosResponse with a ``latest_photos`` list of
            :class:`MarsRoverPhoto`.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            resp = svc.latest_photos("perseverance")
            print(f"{len(resp.latest_photos)} photos from sol {resp.latest_photos[0].sol}")
        """
        params: dict = {}
        if camera is not None:
            params["camera"] = camera.lower()
        data = self.get_request(
            f"{self._PREFIX}/{rover}/latest_photos",
            params=params or None,
        )
        return MarsRoverLatestPhotosResponse(**data)
