from unittest.mock import MagicMock, patch

import pytest

from nasa_apis_wrapper.base import BaseAPI, NasaAPIException
from nasa_apis_wrapper.trek import (
    TrekService,
    TrekCapabilities,
    TrekLayer,
    TrekProduct,
    TrekProductSearchResponse,
    TrekNomenclatureFeature,
    TrekNomenclatureResponse,
    TrekElevation,
    TrekElevationProfile,
    TrekElevationProfilePoint,
    TREK_CRS_GEOGRAPHIC,
    TREK_CRS_MARS_POLAR_N,
)


# ------------------------------------------------------------------
# Test fixtures / mock data
# ------------------------------------------------------------------

CAPABILITIES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Capabilities xmlns="http://www.opengis.net/wmts/1.0"
              xmlns:ows="http://www.opengis.net/ows/1.1"
              version="1.0.0">
  <Contents>
    <Layer>
      <ows:Identifier>Mars_Viking_MDIM21_ClrMosaic_global_232m</ows:Identifier>
      <ows:Title>Mars Viking Color Mosaic</ows:Title>
      <ows:Abstract>Global color mosaic from Viking orbiter data.</ows:Abstract>
      <Format>image/png</Format>
      <Format>image/jpeg</Format>
      <TileMatrixSetLink>
        <TileMatrixSet>urn:ogc:def:crs:EPSG::4326</TileMatrixSet>
      </TileMatrixSetLink>
    </Layer>
    <Layer>
      <ows:Identifier>THEMIS_DayIR_ControlledMosaics_100m_v2</ows:Identifier>
      <ows:Title>THEMIS Day IR</ows:Title>
      <Format>image/png</Format>
      <TileMatrixSetLink>
        <TileMatrixSet>urn:ogc:def:crs:EPSG::4326</TileMatrixSet>
      </TileMatrixSetLink>
      <TileMatrixSetLink>
        <TileMatrixSet>urn:ogc:def:crs:EPSG::32661</TileMatrixSet>
      </TileMatrixSetLink>
    </Layer>
  </Contents>
</Capabilities>"""

FAKE_TILE_BYTES = b"\x89PNG\r\nfake_tile_data"
FAKE_MAP_BYTES = b"\xff\xd8\xff\xe0fake_jpeg_data"

PRODUCT_SEARCH_RESPONSE = {
    "data": [
        {
            "product_label": "Mars_Viking_MDIM21_ClrMosaic_global_232m",
            "title": "Mars Viking Color Mosaic",
            "description": "Global color mosaic from Viking orbiter data.",
            "data_type": "Imagery",
            "resolution": "232m",
            "thumbnail_url": "https://trek.nasa.gov/mars/thumbnails/viking.jpg",
            "projections": ["EPSG:4326"],
        },
        {
            "product_label": "Mars_MOLA_blend200ppx_HRSC_Shade_clon0dd_200mpp_lzw",
            "title": "MOLA Shaded Relief",
            "data_type": "Topography",
            "resolution": "200m",
            "projections": [],
        },
    ],
    "total_count": 42,
    "page": 1,
    "page_size": 10,
}

NOMENCLATURE_RESPONSE = {
    "features": [
        {
            "name": "Olympus Mons",
            "feature_type": "Mons",
            "target": "Mars",
            "center_lat": 18.65,
            "center_lon": 226.2,
            "diameter": 648.0,
            "approval_status": "Adopted",
            "approval_date": "1973",
            "origin": "Classical name for highest volcano.",
        },
        {
            "name": "Olympia Undae",
            "feature_type": "Undae",
            "target": "Mars",
            "center_lat": 81.0,
            "center_lon": 170.0,
            "diameter": 1082.0,
            "approval_status": "Adopted",
        },
    ],
    "total_count": 2,
}

ELEVATION_RESPONSE = {
    "elevation": 21229.0,
    "unit": "m",
    "lat": 18.65,
    "lon": 226.2,
}

ELEVATION_PROFILE_RESPONSE = {
    "points": [
        {"lat": -13.9, "lon": 265.0, "elevation": -3500.0, "distance": 0.0},
        {"lat": -13.9, "lon": 280.0, "elevation": -7500.0, "distance": 740.0},
        {"lat": -13.9, "lon": 320.0, "elevation": -2100.0, "distance": 2960.0},
    ],
    "unit": "m",
    "total_distance": 2960.0,
}


@pytest.fixture
def service():
    return TrekService()


def _mock_bytes(content: bytes, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.content = content
    resp.text = content.decode(errors="replace")
    return resp


# ------------------------------------------------------------------
# Init
# ------------------------------------------------------------------

class TestTrekServiceInit:
    def test_host(self, service):
        assert service.host == "https://trek.nasa.gov"

    def test_no_api_key(self, service):
        assert not service.session.params


# ------------------------------------------------------------------
# WMTS — URL builders
# ------------------------------------------------------------------

class TestTileUrl:
    def test_mars_basic(self, service):
        url = service.tile_url("mars", "Mars_Viking_MDIM21_ClrMosaic_global_232m", zoom=2, row=1, col=3)
        assert "trek.nasa.gov/mars/TrekServices/ws/wmts" in url
        assert "request=GetTile" in url
        assert "layer=Mars_Viking_MDIM21_ClrMosaic_global_232m" in url
        assert "tilematrix=2" in url
        assert "tilerow=1" in url
        assert "tilecol=3" in url

    def test_moon_body(self, service):
        url = service.tile_url("moon", "LRO_WAC_Mosaic_Global_303m", zoom=0, row=0, col=0)
        assert "/moon/TrekServices" in url

    def test_vesta_body(self, service):
        url = service.tile_url("vesta", "Dawn_FC_HAMO_Mosaic_Global_74ppd", zoom=0, row=0, col=0)
        assert "/vesta/TrekServices" in url

    def test_custom_tilematrixset(self, service):
        url = service.tile_url("mars", "layer", zoom=1, row=0, col=0, tilematrixset=TREK_CRS_MARS_POLAR_N)
        assert "32661" in url

    def test_jpeg_format(self, service):
        url = service.tile_url("mars", "layer", zoom=0, row=0, col=0, fmt="image/jpeg")
        assert "image" in url and "jpeg" in url

    def test_wmts_params_present(self, service):
        url = service.tile_url("mars", "layer", zoom=0, row=0, col=0)
        assert "service=WMTS" in url
        assert "version=1.0.0" in url
        assert "style=default" in url


class TestCapabilitiesUrl:
    def test_mars(self, service):
        url = service.capabilities_url("mars")
        assert "/mars/TrekServices/ws/wmts" in url
        assert "GetCapabilities" in url

    def test_moon(self, service):
        assert "/moon/" in service.capabilities_url("moon")

    def test_vesta(self, service):
        assert "/vesta/" in service.capabilities_url("vesta")


# ------------------------------------------------------------------
# WMS — URL builder
# ------------------------------------------------------------------

class TestWmsUrl:
    def test_basic_wms_url(self, service):
        url = service.wms_url(
            body="mars",
            layer="Mars_Viking_MDIM21_ClrMosaic_global_232m",
            bbox="-180,-90,180,90",
            width=1024, height=512,
        )
        assert "/mars/TrekServices/ws/wms" in url
        assert "REQUEST=GetMap" in url
        assert "LAYERS=Mars_Viking_MDIM21_ClrMosaic_global_232m" in url
        assert "WIDTH=1024" in url
        assert "HEIGHT=512" in url
        assert "SRS=EPSG" in url

    def test_wms_version_130_uses_crs(self, service):
        url = service.wms_url("mars", "layer", "-180,-90,180,90", 512, 256, version="1.3.0")
        assert "CRS=" in url
        assert "SRS=" not in url

    def test_wms_jpeg_format(self, service):
        url = service.wms_url("moon", "LRO_WAC_Mosaic_Global_303m", "-180,-90,180,90", 512, 256,
                              fmt="image/jpeg")
        assert "FORMAT=image" in url

    def test_wms_moon_body(self, service):
        url = service.wms_url("moon", "layer", "0,0,10,10", 256, 256)
        assert "/moon/TrekServices/ws/wms" in url


# ------------------------------------------------------------------
# WMTS — HTTP
# ------------------------------------------------------------------

class TestGetTile:
    def test_returns_bytes(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_TILE_BYTES)):
            result = service.get_tile("mars", "Mars_Viking_MDIM21_ClrMosaic_global_232m", zoom=2, row=1, col=3)
        assert result == FAKE_TILE_BYTES

    def test_url_contains_body_and_layer(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_TILE_BYTES)) as mock_get:
            service.get_tile("moon", "LRO_WAC_Mosaic_Global_303m", zoom=1, row=0, col=0)
            called_url = mock_get.call_args[0][0]
            assert "/moon/" in called_url
            assert "LRO_WAC_Mosaic_Global_303m" in called_url

    def test_raises_on_error(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(b"Not found", 404)):
            with pytest.raises(NasaAPIException):
                service.get_tile("vesta", "nonexistent", zoom=0, row=0, col=0)


class TestGetCapabilities:
    def test_returns_capabilities(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(CAPABILITIES_XML.encode())):
            result = service.get_capabilities("mars")
        assert isinstance(result, TrekCapabilities)
        assert result.body == "mars"
        assert len(result.layers) == 2

    def test_layer_fields(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(CAPABILITIES_XML.encode())):
            result = service.get_capabilities("mars")
        layer = result.layers[0]
        assert layer.identifier == "Mars_Viking_MDIM21_ClrMosaic_global_232m"
        assert layer.title == "Mars Viking Color Mosaic"
        assert "image/png" in layer.formats
        assert "image/jpeg" in layer.formats
        assert TREK_CRS_GEOGRAPHIC in layer.tile_matrix_sets

    def test_multiple_tilematrixsets(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(CAPABILITIES_XML.encode())):
            result = service.get_capabilities("mars")
        layer2 = result.layers[1]
        assert len(layer2.tile_matrix_sets) == 2

    def test_empty_capabilities(self, service):
        xml = b'<?xml version="1.0"?><Capabilities xmlns="http://www.opengis.net/wmts/1.0" version="1.0.0"></Capabilities>'
        with patch.object(service.session, "get", return_value=_mock_bytes(xml)):
            result = service.get_capabilities("vesta")
        assert result.layers == []

    def test_raises_on_error(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(b"Server error", 500)):
            with pytest.raises(NasaAPIException):
                service.get_capabilities("mars")


# ------------------------------------------------------------------
# WMS — HTTP
# ------------------------------------------------------------------

class TestGetMap:
    def test_returns_bytes(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_MAP_BYTES)):
            result = service.get_map("mars", "Mars_Viking_MDIM21_ClrMosaic_global_232m",
                                     bbox="-180,-90,180,90", width=1024, height=512)
        assert result == FAKE_MAP_BYTES

    def test_url_contains_getmap(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(FAKE_MAP_BYTES)) as mock_get:
            service.get_map("moon", "LRO_WAC_Mosaic_Global_303m", "-180,-90,180,90", 512, 256)
            url = mock_get.call_args[0][0]
            assert "GetMap" in url
            assert "/moon/" in url

    def test_raises_on_error(self, service):
        with patch.object(service.session, "get", return_value=_mock_bytes(b"Error", 400)):
            with pytest.raises(NasaAPIException):
                service.get_map("mars", "layer", "0,0,1,1", 256, 256)


# ------------------------------------------------------------------
# Product search
# ------------------------------------------------------------------

class TestSearchProducts:
    def test_returns_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PRODUCT_SEARCH_RESPONSE):
            result = service.search_products("mars", "mola")
        assert isinstance(result, TrekProductSearchResponse)
        assert result.total_count == 42
        assert result.page == 1

    def test_products_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PRODUCT_SEARCH_RESPONSE):
            result = service.search_products("mars", "mola")
        p = result.data[0]
        assert isinstance(p, TrekProduct)
        assert p.product_label == "Mars_Viking_MDIM21_ClrMosaic_global_232m"
        assert p.data_type == "Imagery"
        assert p.resolution == "232m"
        assert p.projections == ["EPSG:4326"]

    def test_optional_fields_none(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PRODUCT_SEARCH_RESPONSE):
            result = service.search_products("mars", "mola")
        assert result.data[1].thumbnail_url is None

    def test_passes_params(self, service):
        with patch.object(BaseAPI, "get_request", return_value=PRODUCT_SEARCH_RESPONSE) as mock_get:
            service.search_products("mars", "topography", page=2, page_size=5)
            mock_get.assert_called_once_with(
                "/mars/TrekServices/ws/index/eq/productSearch",
                params={"searchTerm": "topography", "page": 2, "pageSize": 5},
            )


# ------------------------------------------------------------------
# Nomenclature
# ------------------------------------------------------------------

class TestSearchNomenclature:
    def test_returns_response(self, service):
        with patch.object(BaseAPI, "get_request", return_value=NOMENCLATURE_RESPONSE):
            result = service.search_nomenclature("mars", "olympus")
        assert isinstance(result, TrekNomenclatureResponse)
        assert result.total_count == 2
        assert len(result.features) == 2

    def test_feature_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=NOMENCLATURE_RESPONSE):
            result = service.search_nomenclature("mars", "olympus")
        f = result.features[0]
        assert isinstance(f, TrekNomenclatureFeature)
        assert f.name == "Olympus Mons"
        assert f.feature_type == "Mons"
        assert f.center_lat == pytest.approx(18.65)
        assert f.center_lon == pytest.approx(226.2)
        assert f.diameter == pytest.approx(648.0)
        assert f.approval_status == "Adopted"

    def test_optional_origin(self, service):
        with patch.object(BaseAPI, "get_request", return_value=NOMENCLATURE_RESPONSE):
            result = service.search_nomenclature("mars", "olympus")
        assert result.features[1].origin is None

    def test_feature_type_filter_passed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=NOMENCLATURE_RESPONSE) as mock_get:
            service.search_nomenclature("mars", "olympus", feature_type="Mons")
            params = mock_get.call_args[1]["params"]
            assert params["featureType"] == "Mons"

    def test_no_feature_type_filter(self, service):
        with patch.object(BaseAPI, "get_request", return_value=NOMENCLATURE_RESPONSE) as mock_get:
            service.search_nomenclature("moon", "tycho")
            params = mock_get.call_args[1]["params"]
            assert "featureType" not in params

    def test_passes_body_in_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=NOMENCLATURE_RESPONSE) as mock_get:
            service.search_nomenclature("moon", "tycho")
            endpoint = mock_get.call_args[0][0]
            assert "/moon/" in endpoint


# ------------------------------------------------------------------
# Elevation
# ------------------------------------------------------------------

class TestElevation:
    def test_returns_elevation(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ELEVATION_RESPONSE):
            result = service.elevation("mars", lat=18.65, lon=226.2)
        assert isinstance(result, TrekElevation)
        assert result.elevation == pytest.approx(21229.0)
        assert result.unit == "m"
        assert result.lat == pytest.approx(18.65)
        assert result.lon == pytest.approx(226.2)

    def test_passes_coords(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ELEVATION_RESPONSE) as mock_get:
            service.elevation("mars", lat=18.65, lon=226.2)
            params = mock_get.call_args[1]["params"]
            assert params["lat"] == pytest.approx(18.65)
            assert params["lon"] == pytest.approx(226.2)

    def test_passes_body_in_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ELEVATION_RESPONSE) as mock_get:
            service.elevation("moon", lat=0.0, lon=0.0)
            endpoint = mock_get.call_args[0][0]
            assert "/moon/" in endpoint


class TestElevationProfile:
    def test_returns_profile(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ELEVATION_PROFILE_RESPONSE):
            result = service.elevation_profile("mars", -13.9, 265.0, -13.9, 320.0)
        assert isinstance(result, TrekElevationProfile)
        assert result.total_distance == pytest.approx(2960.0)
        assert result.unit == "m"

    def test_points_typed(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ELEVATION_PROFILE_RESPONSE):
            result = service.elevation_profile("mars", -13.9, 265.0, -13.9, 320.0)
        assert len(result.points) == 3
        pt = result.points[0]
        assert isinstance(pt, TrekElevationProfilePoint)
        assert pt.lat == pytest.approx(-13.9)
        assert pt.elevation == pytest.approx(-3500.0)
        assert pt.distance == pytest.approx(0.0)

    def test_passes_all_params(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ELEVATION_PROFILE_RESPONSE) as mock_get:
            service.elevation_profile("mars", -13.9, 265.0, -13.9, 320.0, samples=200)
            params = mock_get.call_args[1]["params"]
            assert params["startLat"] == pytest.approx(-13.9)
            assert params["startLon"] == pytest.approx(265.0)
            assert params["endLat"] == pytest.approx(-13.9)
            assert params["endLon"] == pytest.approx(320.0)
            assert params["samples"] == 200

    def test_passes_body_in_endpoint(self, service):
        with patch.object(BaseAPI, "get_request", return_value=ELEVATION_PROFILE_RESPONSE) as mock_get:
            service.elevation_profile("vesta", 0.0, 0.0, 10.0, 10.0)
            endpoint = mock_get.call_args[0][0]
            assert "/vesta/" in endpoint
