import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import urlencode

from nasa_apis_wrapper.base import BaseAPI, NasaAPIException
from .models import (
    TREK_CRS_GEOGRAPHIC,
    TrekBody,
    TrekCapabilities,
    TrekElevation,
    TrekElevationProfile,
    TrekElevationProfilePoint,
    TrekLayer,
    TrekNomenclatureFeature,
    TrekNomenclatureResponse,
    TrekProduct,
    TrekProductSearchResponse,
    TrekTileFormat,
)


class TrekService(BaseAPI):
    """
    Service for the NASA Vesta/Moon/Mars Trek API.

    Trek provides mapping services for three planetary bodies — Mars, Earth's
    Moon, and the asteroid Vesta — through several complementary endpoints:

    - **WMTS** — standard OGC tile service (PNG/JPEG map tiles).
    - **WMS** — OGC Web Map Service for arbitrary bounding-box image requests.
    - **Product search** — discover available data layers by keyword.
    - **Nomenclature** — search IAU-approved named features (craters, mountains,
      valleys…) with coordinates and descriptions.
    - **Elevation (DEM)** — query elevation at a point or along a profile.

    No API key required.

    Common WMTS layer examples (Mars)::

        "Mars_Viking_MDIM21_ClrMosaic_global_232m"
        "THEMIS_DayIR_ControlledMosaics_100m_v2"
        "Mars_MOLA_blend200ppx_HRSC_Shade_clon0dd_200mpp_lzw"

    Common WMTS layer examples (Moon)::

        "LRO_WAC_Mosaic_Global_303m"
        "LOLA_Shade"

    Common WMTS layer (Vesta)::

        "Dawn_FC_HAMO_Mosaic_Global_74ppd"
    """

    _HOST = "https://trek.nasa.gov"

    def __init__(self):
        super().__init__()
        self.host = self._HOST

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ws(self, body: TrekBody, service: str) -> str:
        """Return the base URL for a Trek web-service path."""
        return f"{self._HOST}/{body}/TrekServices/ws/{service}"

    @staticmethod
    def _local(elem: ET.Element) -> str:
        return elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

    # ------------------------------------------------------------------
    # WMTS — URL builders (no HTTP)
    # ------------------------------------------------------------------

    def tile_url(
        self,
        body: TrekBody,
        layer: str,
        zoom: int,
        row: int,
        col: int,
        tilematrixset: str = TREK_CRS_GEOGRAPHIC,
        fmt: TrekTileFormat = "image/png",
        style: str = "default",
    ) -> str:
        """
        Build a WMTS GetTile URL without making any HTTP request.

        Args:
            body: Planetary body — ``"mars"``, ``"moon"``, or ``"vesta"``.
            layer: Trek layer identifier (from :meth:`get_capabilities` or
                :meth:`search_products`).
            zoom: TileMatrix zoom level. 0 = whole body in one tile.
            row: TileRow index.
            col: TileCol index.
            tilematrixset: OGC CRS identifier. Defaults to
                ``TREK_CRS_GEOGRAPHIC`` (``urn:ogc:def:crs:EPSG::4326``).
            fmt: Image MIME type.
            style: Style identifier, almost always ``"default"``.

        Returns:
            Full WMTS GetTile URL string.
        """
        params = {
            "service": "WMTS",
            "request": "GetTile",
            "version": "1.0.0",
            "layer": layer,
            "style": style,
            "tilematrixset": tilematrixset,
            "tilematrix": zoom,
            "tilerow": row,
            "tilecol": col,
            "format": fmt,
        }
        return f"{self._ws(body, 'wmts')}?{urlencode(params)}"

    def capabilities_url(self, body: TrekBody) -> str:
        """
        Build a WMTS GetCapabilities URL without making any HTTP request.

        Args:
            body: Planetary body.

        Returns:
            Full GetCapabilities URL string.
        """
        return f"{self._ws(body, 'wmts')}?{urlencode({'service': 'WMTS', 'request': 'GetCapabilities'})}"

    # ------------------------------------------------------------------
    # WMS — URL builder (no HTTP)
    # ------------------------------------------------------------------

    def wms_url(
        self,
        body: TrekBody,
        layer: str,
        bbox: str,
        width: int,
        height: int,
        srs: str = "EPSG:4326",
        fmt: TrekTileFormat = "image/jpeg",
        version: str = "1.1.1",
        style: str = "",
    ) -> str:
        """
        Build a WMS GetMap URL without making any HTTP request.

        WMS allows arbitrary bounding boxes and pixel dimensions, unlike WMTS
        which uses a fixed tile grid.

        Args:
            body: Planetary body.
            layer: Trek layer identifier.
            bbox: Bounding box ``"minx,miny,maxx,maxy"`` in the SRS units.
                For geographic (EPSG:4326): ``"-180,-90,180,90"``.
            width: Output image width in pixels.
            height: Output image height in pixels.
            srs: Spatial reference system. Defaults to ``"EPSG:4326"``.
                WMS 1.3.0 uses the ``CRS`` parameter name; 1.1.1 uses ``SRS``.
            fmt: Output image MIME type.
            version: WMS version — ``"1.1.1"`` (default) or ``"1.3.0"``.
            style: Style name, usually empty string for default.

        Returns:
            Full WMS GetMap URL string.

        Example::

            url = service.wms_url(
                body="mars",
                layer="Mars_Viking_MDIM21_ClrMosaic_global_232m",
                bbox="-180,-90,180,90",
                width=1024, height=512,
            )
        """
        crs_key = "CRS" if version == "1.3.0" else "SRS"
        params = {
            "SERVICE": "WMS",
            "REQUEST": "GetMap",
            "VERSION": version,
            "LAYERS": layer,
            "BBOX": bbox,
            crs_key: srs,
            "WIDTH": width,
            "HEIGHT": height,
            "FORMAT": fmt,
            "STYLES": style,
        }
        return f"{self._ws(body, 'wms')}?{urlencode(params)}"

    # ------------------------------------------------------------------
    # WMTS — HTTP
    # ------------------------------------------------------------------

    def get_tile(
        self,
        body: TrekBody,
        layer: str,
        zoom: int,
        row: int,
        col: int,
        tilematrixset: str = TREK_CRS_GEOGRAPHIC,
        fmt: TrekTileFormat = "image/png",
        style: str = "default",
    ) -> bytes:
        """
        Download a single WMTS tile and return its raw bytes.

        All parameters are identical to :meth:`tile_url`. The returned bytes
        can be saved to disk or passed to an imaging library::

            from PIL import Image
            import io

            data = service.get_tile("moon", "LRO_WAC_Mosaic_Global_303m",
                                    zoom=2, row=1, col=3)
            Image.open(io.BytesIO(data)).show()

        Returns:
            Raw image bytes (PNG or JPEG).

        Raises:
            NasaAPIException: If the tile request fails.
        """
        url = self.tile_url(body, layer, zoom, row, col, tilematrixset, fmt, style)
        resp = self.session.get(url)
        if resp.status_code not in range(200, 300):
            raise NasaAPIException(resp.text)
        return resp.content

    def get_capabilities(self, body: TrekBody) -> TrekCapabilities:
        """
        Fetch and parse the WMTS GetCapabilities document for a planetary body.

        Returns all available layers with identifiers, titles, supported formats,
        and tilematrix sets. Use this to discover layer names for :meth:`tile_url`,
        :meth:`get_tile`, and :meth:`wms_url`.

        Args:
            body: Planetary body — ``"mars"``, ``"moon"``, or ``"vesta"``.

        Returns:
            TrekCapabilities with a ``layers`` list of :class:`TrekLayer`.

        Raises:
            NasaAPIException: If the request fails.
        """
        url = self.capabilities_url(body)
        resp = self.session.get(url)
        if resp.status_code not in range(200, 300):
            raise NasaAPIException(resp.text)
        return self._parse_capabilities(body, resp.text)

    # ------------------------------------------------------------------
    # WMS — HTTP
    # ------------------------------------------------------------------

    def get_map(
        self,
        body: TrekBody,
        layer: str,
        bbox: str,
        width: int,
        height: int,
        srs: str = "EPSG:4326",
        fmt: TrekTileFormat = "image/jpeg",
        version: str = "1.1.1",
        style: str = "",
    ) -> bytes:
        """
        Request a WMS map image and return its raw bytes.

        All parameters are identical to :meth:`wms_url`.

        Returns:
            Raw image bytes (JPEG or PNG).

        Raises:
            NasaAPIException: If the request fails.

        Example::

            img = service.get_map(
                body="mars",
                layer="Mars_Viking_MDIM21_ClrMosaic_global_232m",
                bbox="-180,-90,180,90",
                width=2048, height=1024,
            )
            with open("mars_globe.jpg", "wb") as f:
                f.write(img)
        """
        url = self.wms_url(body, layer, bbox, width, height, srs, fmt, version, style)
        resp = self.session.get(url)
        if resp.status_code not in range(200, 300):
            raise NasaAPIException(resp.text)
        return resp.content

    # ------------------------------------------------------------------
    # Product search
    # ------------------------------------------------------------------

    def search_products(
        self,
        body: TrekBody,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ) -> TrekProductSearchResponse:
        """
        Search available data products (layers) for a planetary body.

        Returns products whose title or description match the query. The
        ``product_label`` field of each result can be used directly as the
        ``layer`` argument in :meth:`tile_url` and :meth:`get_tile`.

        Args:
            body: Planetary body.
            query: Free-text search term (e.g. ``"mola"``, ``"geology"``).
            page: Page number (1-based).
            page_size: Results per page.

        Returns:
            TrekProductSearchResponse with a ``data`` list of
            :class:`TrekProduct`.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.search_products("mars", "topography")
            for product in result.data:
                print(product.product_label, product.resolution)
        """
        data = self.get_request(
            f"/{body}/TrekServices/ws/index/eq/productSearch",
            params={"searchTerm": query, "page": page, "pageSize": page_size},
        )
        return TrekProductSearchResponse(**data)

    # ------------------------------------------------------------------
    # Nomenclature
    # ------------------------------------------------------------------

    def search_nomenclature(
        self,
        body: TrekBody,
        query: str,
        feature_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TrekNomenclatureResponse:
        """
        Search IAU-approved named surface features for a planetary body.

        Returns craters, mountains, valleys, plains, and other named features
        matching the query. Coordinates are in decimal degrees (planetocentric).

        Args:
            body: Planetary body.
            query: Feature name or fragment (e.g. ``"olympus"``, ``"hellas"``).
            feature_type: Optional IAU descriptor to filter by (e.g.
                ``"Crater"``, ``"Mons"``, ``"Vallis"``, ``"Planitia"``).
            page: Page number (1-based).
            page_size: Results per page.

        Returns:
            TrekNomenclatureResponse with a ``features`` list of
            :class:`TrekNomenclatureFeature`.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            result = service.search_nomenclature("mars", "olympus")
            for feature in result.features:
                print(feature.name, feature.feature_type,
                      feature.center_lat, feature.center_lon)
        """
        params: dict = {"searchTerm": query, "page": page, "pageSize": page_size}
        if feature_type is not None:
            params["featureType"] = feature_type
        data = self.get_request(
            f"/{body}/TrekServices/ws/nomenclature/search",
            params=params,
        )
        return TrekNomenclatureResponse(**data)

    # ------------------------------------------------------------------
    # Elevation / DEM
    # ------------------------------------------------------------------

    def elevation(self, body: TrekBody, lat: float, lon: float) -> TrekElevation:
        """
        Query the elevation at a single point on a planetary surface.

        Elevation values are relative to the planetary datum: areoid for Mars,
        selenoid for the Moon, and reference ellipsoid for Vesta.

        Args:
            body: Planetary body.
            lat: Latitude in decimal degrees (planetocentric).
            lon: Longitude in decimal degrees (0–360 East or -180–180).

        Returns:
            TrekElevation with the ``elevation`` value in metres.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            # Olympus Mons summit
            result = service.elevation("mars", lat=18.65, lon=226.2)
            print(result.elevation, result.unit)   # ~21229.0 m
        """
        data = self.get_request(
            f"/{body}/TrekServices/ws/dem/point",
            params={"lat": lat, "lon": lon},
        )
        return TrekElevation(**data)

    def elevation_profile(
        self,
        body: TrekBody,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        samples: int = 100,
    ) -> TrekElevationProfile:
        """
        Query elevation along a great-circle path between two surface points.

        Args:
            body: Planetary body.
            start_lat: Start latitude in decimal degrees.
            start_lon: Start longitude in decimal degrees.
            end_lat: End latitude in decimal degrees.
            end_lon: End longitude in decimal degrees.
            samples: Number of sample points along the path (default 100).

        Returns:
            TrekElevationProfile with a ``points`` list of
            :class:`TrekElevationProfilePoint` at regular intervals, plus
            ``total_distance`` in kilometres.

        Raises:
            NasaAPIException: If the request fails.

        Example::

            # Profile across Valles Marineris
            profile = service.elevation_profile(
                "mars",
                start_lat=-13.9, start_lon=265.0,
                end_lat=-13.9, end_lon=320.0,
                samples=200,
            )
            for pt in profile.points:
                print(pt.distance, pt.elevation)
        """
        data = self.get_request(
            f"/{body}/TrekServices/ws/dem/profile",
            params={
                "startLat": start_lat,
                "startLon": start_lon,
                "endLat": end_lat,
                "endLon": end_lon,
                "samples": samples,
            },
        )
        return TrekElevationProfile(**data)

    # ------------------------------------------------------------------
    # Internal XML parser
    # ------------------------------------------------------------------

    @classmethod
    def _parse_capabilities(cls, body: str, xml_text: str) -> TrekCapabilities:
        root = ET.fromstring(xml_text)
        local = cls._local

        contents = next(
            (el for el in root.iter() if local(el) == "Contents"), None
        )
        if contents is None:
            return TrekCapabilities(body=body, layers=[])

        layers: list[TrekLayer] = []
        for layer_elem in contents:
            if local(layer_elem) != "Layer":
                continue

            identifier: str | None = None
            title: str | None = None
            abstract: str | None = None
            formats: list[str] = []
            tile_matrix_sets: list[str] = []

            for child in layer_elem:
                tag = local(child)
                if tag == "Identifier":
                    identifier = child.text
                elif tag == "Title":
                    title = child.text
                elif tag == "Abstract":
                    abstract = child.text
                elif tag == "Format" and child.text:
                    formats.append(child.text.strip())
                elif tag == "TileMatrixSetLink":
                    for sub in child:
                        if local(sub) == "TileMatrixSet" and sub.text:
                            tile_matrix_sets.append(sub.text.strip())

            if identifier:
                layers.append(TrekLayer(
                    identifier=identifier,
                    title=title,
                    abstract=abstract,
                    formats=formats,
                    tile_matrix_sets=tile_matrix_sets,
                ))

        return TrekCapabilities(body=body, layers=layers)
