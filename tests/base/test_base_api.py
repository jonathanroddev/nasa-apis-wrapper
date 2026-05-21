import pytest
import responses
from requests.exceptions import ConnectionError, Timeout

from nasa_apis_wrapper import BaseAPI, NasaAPIException


class TestBaseAPI:
    @responses.activate
    def test_get_request(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"result": "success"},
            status=200,
        )
        result = base_api.get_request("/test")
        assert result["result"] == "success"

    @responses.activate
    def test_post_request(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.POST,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"result": "success"},
            status=200,
        )
        result = base_api.post_request("/test", {"test": "test"})
        assert result["result"] == "success"

    # ------------------------------------------------------------------
    # Error: non-2xx JSON responses
    # ------------------------------------------------------------------

    @responses.activate
    def test_get_raises_on_non_2xx(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"error": {"message": "API key invalid"}},
            status=403,
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.get_request("/test")
        assert "API key invalid" in str(exc_info.value)
        assert "403" in str(exc_info.value)

    @responses.activate
    def test_post_raises_on_non_2xx(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.POST,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"msg": "Rate limit exceeded"},
            status=429,
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.post_request("/test", {})
        assert "Rate limit exceeded" in str(exc_info.value)

    @responses.activate
    def test_error_extracts_msg_field(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"msg": "Not found"},
            status=404,
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.get_request("/test")
        assert "Not found" in str(exc_info.value)

    # ------------------------------------------------------------------
    # Error: HTML responses (proxy / gateway errors)
    # ------------------------------------------------------------------

    @responses.activate
    def test_get_strips_html_from_error(self) -> None:
        base_api = BaseAPI("api_key")
        html = "<html><body><h1>No such app</h1><p>The app does not exist.</p></body></html>"
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            body=html,
            status=404,
            content_type="text/html",
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.get_request("/test")
        msg = str(exc_info.value)
        assert "<html>" not in msg
        assert "<h1>" not in msg
        assert "No such app" in msg
        assert "404" in msg

    @responses.activate
    def test_post_strips_html_from_error(self) -> None:
        base_api = BaseAPI("api_key")
        html = "<html><body>Internal Server Error</body></html>"
        responses.add(
            responses.POST,
            "https://api.nasa.gov/test?api_key=api_key",
            body=html,
            status=500,
            content_type="text/html",
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.post_request("/test", {})
        msg = str(exc_info.value)
        assert "<html>" not in msg
        assert "500" in msg

    # ------------------------------------------------------------------
    # Error: network failures
    # ------------------------------------------------------------------

    @responses.activate
    def test_get_wraps_connection_error(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            body=ConnectionError("Connection refused"),
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.get_request("/test")
        assert "Request failed" in str(exc_info.value)

    @responses.activate
    def test_get_wraps_timeout(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            body=Timeout("Read timed out"),
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.get_request("/test")
        assert "Request failed" in str(exc_info.value)

    @responses.activate
    def test_post_wraps_connection_error(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.POST,
            "https://api.nasa.gov/test?api_key=api_key",
            body=ConnectionError("Connection refused"),
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.post_request("/test", {})
        assert "Request failed" in str(exc_info.value)

    # ------------------------------------------------------------------
    # Error: 2xx but non-JSON body
    # ------------------------------------------------------------------

    @responses.activate
    def test_get_raises_on_non_json_200(self) -> None:
        base_api = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            body="not json at all",
            status=200,
            content_type="text/plain",
        )
        with pytest.raises(NasaAPIException) as exc_info:
            base_api.get_request("/test")
        assert "non-JSON" in str(exc_info.value)
