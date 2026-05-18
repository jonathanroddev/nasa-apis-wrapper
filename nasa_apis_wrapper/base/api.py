from typing import Any, Optional, Type, TypeVar

from requests import Session

T = TypeVar('T')


class NasaAPIException(Exception):
    """Raised when a NASA API request fails (non-2xx response)."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BaseAPI:
    """Base class for all NASA API services. Manages the HTTP session and API key."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: NASA API key. Required for most APIs; get one at https://api.nasa.gov/.
                     APIs that do not require authentication (e.g. EONET) can omit this.
        """
        self.host: str = "https://api.nasa.gov"
        self.session: Session = Session()
        self.session.headers.update({"Accept": "application/json"})
        if api_key:
            self.session.params = {"api_key": api_key}

    def get_request(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """
        Send a GET request and return the parsed JSON response.

        Args:
            endpoint: API path relative to the host (e.g. ``/planetary/apod``).
            params: Optional query parameters.

        Raises:
            NasaAPIException: If the response status code is not 2xx.
        """
        url = f"{self.host}{endpoint}"
        req = self.session.get(url, params=params)
        if req.status_code not in range(200, 300):
            raise NasaAPIException(req.text)
        return req.json()

    def post_request(self, endpoint: str, json_data: dict) -> Any:
        """
        Send a POST request and return the parsed JSON response.

        Args:
            endpoint: API path relative to the host.
            json_data: Request body serialized as JSON.

        Raises:
            NasaAPIException: If the response status code is not 2xx.
        """
        url = f"{self.host}{endpoint}"
        req = self.session.post(url, json=json_data)
        if req.status_code not in range(200, 300):
            raise NasaAPIException(req.text)
        return req.json()

    def _parse_list(self, endpoint: str, model: Type[T], params: Optional[dict] = None) -> list[T]:
        """Fetch a list endpoint and deserialize each item into *model*."""
        return [model(**item) for item in self.get_request(endpoint, params)]

    def _parse_one(self, endpoint: str, model: Type[T], params: Optional[dict] = None) -> T:
        """Fetch a single-object endpoint and deserialize the response into *model*."""
        return model(**self.get_request(endpoint, params))
