import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import urlencode

from nasa_apis_wrapper.base import BaseAPI, NasaAPIException
from .models import GIBSDomains, GIBSProjection, GIBSTileFormat, GIBSWMSFormat, GIBSDataType


class GIBSService(BaseAPI):
    """
    Service for the NASA Global Imagery Browse Services (GIBS) WMTS/WMS API.

    GIBS provides satellite imagery tiles for Earth observation. Unlike other
    NASA APIs in this library, responses are **image bytes** (JPEG/PNG tiles)
    or XML — not JSON. No API key required.

    Two usage patterns:

    - **URL builders** — :meth:`tile_url` and :meth:`wms_url` construct URLs
      without making any HTTP request. Useful for feeding into mapping libraries
      (Leaflet, OpenLayers, deck.gl) or downloading images manually.
    - **Direct download** — :meth:`get_tile` downloads a tile and returns
      raw bytes ready to save or pass to Pillow/NumPy.

    Common layers::

        "MODIS_Terra_CorrectedReflectance_TrueColor"  # daily true-colour
        "MODIS_Aqua_CorrectedReflectance_TrueColor"   # daily true-colour (Aqua)
        "VIIRS_SNPP_CorrectedReflectance_TrueColor"   # VIIRS daily
        "OMI_Aerosol_Index"                            # UV aerosol index
        "MERRA2_2m_Air_Temperature_Monthly"            # monthly temperature
    """

    _BASE = "https://gibs.earthdata.nasa.gov"

    def __init__(self):
        super().__init__()  # GIBS does not require an API key
        self.host = self._BASE

    # ------------------------------------------------------------------
    # URL builders (no HTTP request)
    # ------------------------------------------------------------------

    def tile_url(
        self,
        layer: str,
        tile_matrix_set: str,
        zoom: int,
        row: int,
        col: int,
        date: Optional[str] = None,
        projection: GIBSProjection = "EPSG:4326",
        fmt: GIBSTileFormat = "jpg",
        data_type: GIBSDataType = "best",
    ) -> str:
        """
        Build a WMTS REST tile URL without making any HTTP request.

        Args:
            layer: GIBS layer identifier, e.g.
                ``"MODIS_Terra_CorrectedReflectance_TrueColor"``.
            tile_matrix_set: Resolution identifier, e.g. ``"250m"``, ``"1km"``,
                ``"GoogleMapsCompatible_Level12"``.
            zoom: Tile zoom level (TileMatrix). 0 = world in one tile.
            row: Tile row index (TileRow).
            col: Tile column index (TileCol).
            date: Date in ``"YYYY-MM-DD"`` format. Omit for static layers.
            projection: Coordinate reference system. Defaults to
                ``"EPSG:4326"`` (geographic). Use ``"EPSG:3857"`` for
                Web Mercator (Google Maps / Leaflet compatible).
            fmt: Image format. ``"jpg"`` for true-colour imagery;
                ``"png"`` for scientific data with transparency.
            data_type: Dataset tier. ``"best"`` (default) serves the
                most processed available data; ``"nrt"`` for near-real-time.

        Returns:
            Full URL string. Pass directly to a mapping library or
            :meth:`get_tile`.

        Example::

            url = service.tile_url(
                layer="MODIS_Terra_CorrectedReflectance_TrueColor",
                tile_matrix_set="250m",
                zoom=3, row=2, col=5,
                date="2024-01-15",
            )
        """
        epsg = self._epsg_path(projection)
        date_segment = f"{date}/" if date else ""
        return (
            f"{self._BASE}/wmts/{epsg}/{data_type}/{layer}/default"
            f"/{date_segment}{tile_matrix_set}/{zoom}/{row}/{col}.{fmt}"
        )

    def wms_url(
        self,
        layer: str,
        bbox: str,
        width: int,
        height: int,
        date: Optional[str] = None,
        projection: GIBSProjection = "EPSG:4326",
        fmt: GIBSWMSFormat = "image/jpeg",
        version: str = "1.1.1",
        data_type: GIBSDataType = "best",
    ) -> str:
        """
        Build a WMS GetMap URL without making any HTTP request.

        WMS is more flexible than WMTS tiles — it accepts arbitrary bounding
        boxes and pixel dimensions, and can composite multiple layers.

        Args:
            layer: GIBS layer identifier.
            bbox: Bounding box as ``"minx,miny,maxx,maxy"`` in the CRS units.
                Example for geographic: ``"-180,-90,180,90"``.
            width: Output image width in pixels.
            height: Output image height in pixels.
            date: Date in ``"YYYY-MM-DD"`` format. Omit for static layers.
            projection: Coordinate reference system. Defaults to ``"EPSG:4326"``.
            fmt: MIME type for the output image.
            version: WMS version. ``"1.1.1"`` (default) or ``"1.3.0"``.
            data_type: Dataset tier. Defaults to ``"best"``.

        Returns:
            Full WMS GetMap URL string.

        Example::

            url = service.wms_url(
                layer="MODIS_Terra_CorrectedReflectance_TrueColor",
                bbox="-130,24,-60,50",
                width=1024, height=512,
                date="2024-01-15",
            )
        """
        epsg = self._epsg_path(projection)
        # WMS 1.3.0 uses CRS instead of SRS
        crs_param = "CRS" if version == "1.3.0" else "SRS"
        params = {
            "SERVICE": "WMS",
            "REQUEST": "GetMap",
            "VERSION": version,
            "LAYERS": layer,
            "BBOX": bbox,
            crs_param: projection,
            "WIDTH": width,
            "HEIGHT": height,
            "FORMAT": fmt,
            "STYLE": "",
        }
        if date:
            params["TIME"] = date
        base = f"{self._BASE}/wms/{epsg}/{data_type}/wms.cgi"
        return f"{base}?{urlencode(params)}"

    # ------------------------------------------------------------------
    # HTTP methods
    # ------------------------------------------------------------------

    def get_tile(
        self,
        layer: str,
        tile_matrix_set: str,
        zoom: int,
        row: int,
        col: int,
        date: Optional[str] = None,
        projection: GIBSProjection = "EPSG:4326",
        fmt: GIBSTileFormat = "jpg",
        data_type: GIBSDataType = "best",
    ) -> bytes:
        """
        Download a single WMTS tile and return its raw bytes.

        All parameters are identical to :meth:`tile_url`. The returned bytes
        can be written directly to a file or passed to imaging libraries::

            from PIL import Image
            import io

            tile_bytes = service.get_tile(
                layer="MODIS_Terra_CorrectedReflectance_TrueColor",
                tile_matrix_set="250m",
                zoom=3, row=2, col=5,
                date="2024-01-15",
            )
            image = Image.open(io.BytesIO(tile_bytes))

        Returns:
            Raw image bytes (JPEG or PNG depending on ``fmt``).

        Raises:
            NasaAPIException: If the tile request fails.
        """
        url = self.tile_url(layer, tile_matrix_set, zoom, row, col, date, projection, fmt, data_type)
        resp = self.session.get(url)
        if resp.status_code not in range(200, 300):
            raise NasaAPIException(resp.text)
        return resp.content

    def describe_domains(
        self,
        layer: str,
        tile_matrix_set: str,
        projection: GIBSProjection = "EPSG:4326",
        time_range: str = "all",
        data_type: GIBSDataType = "best",
    ) -> GIBSDomains:
        """
        Query which dates have imagery available for a given layer.

        Args:
            layer: GIBS layer identifier.
            tile_matrix_set: Resolution identifier, e.g. ``"250m"``.
            projection: Coordinate reference system. Defaults to ``"EPSG:4326"``.
            time_range: Time range to query. Use ``"all"`` (default) to get
                all available dates, or an ISO 8601 interval like
                ``"2024-01-01/2024-12-31"`` to restrict the window.
            data_type: Dataset tier. Defaults to ``"best"``.

        Returns:
            GIBSDomains with the layer's temporal availability. Use
            :attr:`~GIBSDomains.dates` for a list of individual dates or
            :attr:`~GIBSDomains.start_date` / :attr:`~GIBSDomains.end_date`
            for the bounds.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            domains = service.describe_domains(
                layer="MODIS_Terra_CorrectedReflectance_TrueColor",
                tile_matrix_set="250m",
            )
            print(domains.start_date)  # "2000-02-24"
            print(domains.end_date)    # "2024-01-15"
        """
        epsg = self._epsg_path(projection)
        url = f"{self._BASE}/wmts/{epsg}/{data_type}/wmts.cgi"
        params = {
            "SERVICE": "WMTS",
            "REQUEST": "DescribeDomains",
            "VERSION": "1.0.0",
            "LAYER": layer,
            "TILEMATRIXSET": tile_matrix_set,
            "TIME": time_range,
        }
        resp = self.session.get(url, params=params)
        if resp.status_code not in range(200, 300):
            raise NasaAPIException(resp.text)
        return self._parse_domains(layer, resp.text)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _epsg_path(projection: str) -> str:
        """Convert 'EPSG:4326' to 'epsg4326' for URL paths."""
        return projection.lower().replace(":", "")

    @staticmethod
    def _parse_domains(layer: str, xml_text: str) -> GIBSDomains:
        root = ET.fromstring(xml_text)
        # Tags may carry a namespace like {http://...}Domain — search by local name
        for elem in root.iter():
            local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            parent_local = ""
            # We want the Domain element that is a child of DimensionDomain
            if local == "Domain" and elem.text:
                domain_text = elem.text.strip()
                if domain_text:
                    return GIBSDomains(layer=layer, domain=domain_text)
        return GIBSDomains(layer=layer, domain="")
