from typing import Optional

from nasa_apis_wrapper.base import BaseAPI, NasaAPIException
from .models import EarthAsset


class EarthService(BaseAPI):
    """
    Service for the NASA Earth (Landsat 8) API.

    Provides access to Landsat 8 satellite imagery and asset metadata for any
    point on Earth's surface. Images are provided by Google Earth Engine and
    cover the full globe with a roughly 16-day revisit cycle since April 2013.

    Requires an API key.

    Typical workflow:
    1. Call :meth:`assets` to find the closest available image date for a
       location (and optionally get its cloud score).
    2. Call :meth:`imagery` with the confirmed date to download the PNG tile.

    Example::

        svc = EarthService(api_key="YOUR_KEY")
        asset = svc.assets(lat=29.78, lon=-95.33, date="2014-02-01")
        print(asset.date, asset.cloud_score)

        png = svc.imagery(lat=29.78, lon=-95.33, date=asset.date)
        with open("houston.png", "wb") as f:
            f.write(png)
    """

    def imagery(
        self,
        lat: float,
        lon: float,
        date: Optional[str] = None,
        dim: float = 0.025,
        cloud_score: bool = False,
    ) -> bytes:
        """
        Download a Landsat 8 PNG image centred on a coordinate.

        The returned image is a 3-band (RGB) PNG tile covering a square area of
        ``dim × dim`` degrees around the given point.

        Args:
            lat: Latitude in decimal degrees (−90 to 90).
            lon: Longitude in decimal degrees (−180 to 180).
            date: Most recent image date to use, in ``"YYYY-MM-DD"`` format.
                If omitted the API returns the most recent available image.
            dim: Width and height of the bounding box in degrees. Defaults to
                ``0.025`` (~2.5 km at the equator).
            cloud_score: If ``True``, the API calculates a cloud-cover score
                before returning. This makes the request slower but lets you
                reject heavily clouded images.

        Returns:
            Raw PNG image bytes.

        Raises:
            NasaAPIException: If no imagery is available or the request fails.

        Example::

            png = svc.imagery(lat=48.86, lon=2.35, date="2021-06-15")
            with open("paris.png", "wb") as f:
                f.write(png)
        """
        params: dict = {"lat": lat, "lon": lon, "dim": dim}
        if date:
            params["date"] = date
        if cloud_score:
            params["cloud_score"] = "True"
        resp = self.session.get(f"{self.host}/planetary/earth/imagery", params=params)
        if resp.status_code not in range(200, 300):
            raise NasaAPIException(resp.text)
        return resp.content

    def assets(
        self,
        lat: float,
        lon: float,
        date: str,
        dim: float = 0.025,
    ) -> EarthAsset:
        """
        Retrieve metadata for the closest available Landsat 8 image.

        Returns the actual capture date, a GCS URL to the full GeoTIFF, and
        optionally a cloud-cover score. Useful for checking image availability
        before calling :meth:`imagery`.

        Args:
            lat: Latitude in decimal degrees.
            lon: Longitude in decimal degrees.
            date: Target date in ``"YYYY-MM-DD"`` format. The API returns the
                most recent image on or before this date.
            dim: Bounding-box size in degrees. Defaults to ``0.025``.

        Returns:
            EarthAsset with ``date``, ``url``, and optional ``cloud_score``.

        Raises:
            NasaAPIException: If no asset exists for the given parameters.

        Example::

            asset = svc.assets(lat=29.78, lon=-95.33, date="2018-01-01")
            print(asset.date, asset.url)
        """
        data = self.get_request(
            "/planetary/earth/assets",
            params={"lat": lat, "lon": lon, "date": date, "dim": dim},
        )
        return EarthAsset(**data)
