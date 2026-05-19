from unittest.mock import MagicMock, patch

import pytest

from nasa_apis_wrapper import GIBSService, NasaAPIException

LAYER = "MODIS_Terra_CorrectedReflectance_TrueColor"
TMS = "250m"

DOMAINS_XML_COMMA = """<?xml version="1.0" encoding="UTF-8"?>
<Domains xmlns="http://earthdata.nasa.gov/schema/DescribeDomainsResponse">
  <DimensionDomain>
    <Identifier>TIME</Identifier>
    <Domain>2000-02-24,2000-02-26,2024-01-15</Domain>
  </DimensionDomain>
</Domains>"""

DOMAINS_XML_INTERVAL = """<?xml version="1.0" encoding="UTF-8"?>
<Domains xmlns="http://earthdata.nasa.gov/schema/DescribeDomainsResponse">
  <DimensionDomain>
    <Identifier>TIME</Identifier>
    <Domain>2000-02-24/2024-01-15/P1D</Domain>
  </DimensionDomain>
</Domains>"""


class TestGIBSService:

    # ------------------------------------------------------------------
    # URL builders
    # ------------------------------------------------------------------

    def test_tile_url_with_date(self) -> None:
        url = GIBSService().tile_url(LAYER, TMS, zoom=3, row=2, col=5, date="2024-01-15")
        assert url == (
            "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best"
            f"/{LAYER}/default/2024-01-15/{TMS}/3/2/5.jpg"
        )

    def test_tile_url_without_date(self) -> None:
        url = GIBSService().tile_url(LAYER, TMS, zoom=0, row=0, col=0)
        assert "/default/250m/0/0/0.jpg" in url
        assert "default/2024" not in url  # no date segment

    def test_tile_url_web_mercator(self) -> None:
        url = GIBSService().tile_url(
            LAYER, "GoogleMapsCompatible_Level12",
            zoom=5, row=10, col=20,
            date="2024-06-01",
            projection="EPSG:3857",
            fmt="png",
        )
        assert "/wmts/epsg3857/best/" in url
        assert url.endswith(".png")

    def test_tile_url_nrt_data_type(self) -> None:
        url = GIBSService().tile_url(LAYER, TMS, zoom=0, row=0, col=0, data_type="nrt")
        assert "/wmts/epsg4326/nrt/" in url

    def test_wms_url_v111(self) -> None:
        url = GIBSService().wms_url(
            layer=LAYER,
            bbox="-130,24,-60,50",
            width=1024, height=512,
            date="2024-01-15",
        )
        assert "REQUEST=GetMap" in url
        assert "SRS=EPSG%3A4326" in url
        assert "TIME=2024-01-15" in url
        assert "WIDTH=1024" in url

    def test_wms_url_v130_uses_crs(self) -> None:
        url = GIBSService().wms_url(
            layer=LAYER, bbox="-180,-90,180,90",
            width=512, height=256,
            version="1.3.0",
        )
        assert "CRS=EPSG%3A4326" in url
        assert "SRS" not in url

    def test_wms_url_no_date(self) -> None:
        url = GIBSService().wms_url(layer=LAYER, bbox="-180,-90,180,90", width=256, height=128)
        assert "TIME" not in url

    # ------------------------------------------------------------------
    # get_tile (mocks session.get)
    # ------------------------------------------------------------------

    def test_get_tile_returns_bytes(self) -> None:
        fake_bytes = b"\xff\xd8\xff"  # JPEG magic bytes
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = fake_bytes

        service = GIBSService()
        with patch.object(service.session, "get", return_value=mock_resp):
            result = service.get_tile(LAYER, TMS, zoom=3, row=2, col=5, date="2024-01-15")

        assert result == fake_bytes

    def test_get_tile_raises_on_error(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Layer not found"

        service = GIBSService()
        with patch.object(service.session, "get", return_value=mock_resp):
            with pytest.raises(NasaAPIException, match="Layer not found"):
                service.get_tile(LAYER, TMS, zoom=0, row=0, col=0)

    # ------------------------------------------------------------------
    # describe_domains
    # ------------------------------------------------------------------

    def test_describe_domains_comma_separated(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = DOMAINS_XML_COMMA

        service = GIBSService()
        with patch.object(service.session, "get", return_value=mock_resp):
            result = service.describe_domains(LAYER, TMS)

        assert result.layer == LAYER
        assert not result.is_interval
        assert result.dates == ["2000-02-24", "2000-02-26", "2024-01-15"]
        assert result.start_date == "2000-02-24"
        assert result.end_date == "2024-01-15"

    def test_describe_domains_interval(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = DOMAINS_XML_INTERVAL

        service = GIBSService()
        with patch.object(service.session, "get", return_value=mock_resp):
            result = service.describe_domains(LAYER, TMS)

        assert result.is_interval
        assert result.dates is None
        assert result.start_date == "2000-02-24"
        assert result.end_date == "2024-01-15"

    def test_no_api_key_required(self) -> None:
        service = GIBSService()
        assert service.host == "https://gibs.earthdata.nasa.gov"
        assert "api_key" not in (service.session.params or {})
