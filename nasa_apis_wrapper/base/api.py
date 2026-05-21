import re
from typing import Any, Optional, Type, TypeVar

from requests import Session
from requests.exceptions import RequestException

T = TypeVar('T')


class NasaAPIException(Exception):
    """Raised when a NASA API request fails (non-2xx response or network error)."""

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
            NasaAPIException: On non-2xx responses, network errors, timeouts,
                or unexpected non-JSON payloads.
        """
        url = f"{self.host}{endpoint}"
        try:
            req = self.session.get(url, params=params, timeout=30)
        except RequestException as exc:
            raise NasaAPIException(f"Request failed: {exc}") from exc
        if req.status_code not in range(200, 300):
            raise NasaAPIException(_extract_error(req))
        try:
            return req.json()
        except ValueError as exc:
            raise NasaAPIException(f"Unexpected non-JSON response from {url}") from exc

    def post_request(self, endpoint: str, json_data: dict) -> Any:
        """
        Send a POST request and return the parsed JSON response.

        Args:
            endpoint: API path relative to the host.
            json_data: Request body serialized as JSON.

        Raises:
            NasaAPIException: On non-2xx responses, network errors, or
                unexpected non-JSON payloads.
        """
        url = f"{self.host}{endpoint}"
        try:
            req = self.session.post(url, json=json_data, timeout=30)
        except RequestException as exc:
            raise NasaAPIException(f"Request failed: {exc}") from exc
        if req.status_code not in range(200, 300):
            raise NasaAPIException(_extract_error(req))
        try:
            return req.json()
        except ValueError as exc:
            raise NasaAPIException(f"Unexpected non-JSON response from {url}") from exc

    def _parse_list(self, endpoint: str, model: Type[T], params: Optional[dict] = None) -> list[T]:
        """Fetch a list endpoint and deserialize each item into *model*."""
        return [model(**item) for item in self.get_request(endpoint, params)]

    def _parse_one(self, endpoint: str, model: Type[T], params: Optional[dict] = None) -> T:
        """Fetch a single-object endpoint and deserialize the response into *model*."""
        return model(**self.get_request(endpoint, params))


def _extract_error(resp: Any) -> str:
    """
    Build a clean, human-readable error message from a failed HTTP response.

    Tries JSON first (NASA APIs often return ``{"error": {"message": "..."}}``,
    ``{"msg": "..."}`` or ``{"error": "..."}``). Falls back to stripping HTML
    tags so that proxy error pages (Heroku, Cloudflare, etc.) don't dump raw
    markup into the exception message.
    """
    content_type = resp.headers.get("Content-Type", "")
    if "json" in content_type:
        try:
            data = resp.json()
            msg = (
                (data.get("error") or {}).get("message")
                or data.get("msg")
                or data.get("error")
                or data.get("message")
            )
            if isinstance(msg, str) and msg:
                return f"HTTP {resp.status_code}: {msg}"
        except ValueError:
            pass

    # Strip HTML tags for cleaner messages from proxy error pages
    text = re.sub(r"<[^>]+>", " ", resp.text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text[:300]
    return f"HTTP {resp.status_code}: {text}" if text else f"HTTP {resp.status_code}"
