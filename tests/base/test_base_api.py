import json

import pytest
import responses

from nasa_apis_wrapper import BaseAPI, NasaAPIException


class TestBaseAPI:
    @responses.activate
    def test_get_request(self) -> None:
        base_api: BaseAPI = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"result": "success"},
            status=200,
        )
        result = base_api.get_request("/test")
        assert result
        assert "result" in result
        assert json.loads(result)["result"] == "success"

    @responses.activate
    def test_get_request_should_raise_custom_exception(self) -> None:
        base_api: BaseAPI = BaseAPI("api_key")
        responses.add(
            responses.GET,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"result": "Unauthorized"},
            status=401,
        )
        with pytest.raises(NasaAPIException) as ne:
            result = base_api.get_request("/test")
        assert str(ne.value) == '{"result": "Unauthorized"}'

    @responses.activate
    def test_post_request(self) -> None:
        base_api: BaseAPI = BaseAPI("api_key")
        responses.add(
            responses.POST,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"result": "success"},
            status=200,
        )
        result = base_api.post_request("/test", {"test": "test"})
        assert result
        assert "result" in result
        assert json.loads(result)["result"] == "success"

    @responses.activate
    def test_post_request_should_raise_custom_exception(self) -> None:
        base_api: BaseAPI = BaseAPI("api_key")
        responses.add(
            responses.POST,
            "https://api.nasa.gov/test?api_key=api_key",
            json={"result": "Unauthorized"},
            status=401,
        )
        with pytest.raises(NasaAPIException) as ne:
            result = base_api.post_request("/test", {"test": "test"})
        assert str(ne.value) == '{"result": "Unauthorized"}'
