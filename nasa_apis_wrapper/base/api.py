"""
Provides the base API class for interacting with NASA APIs.

Classes:
    BaseAPI: Provides a basic implementation for interacting with NASA APIs.
    NasaAPIException: Represents an exception that occurs when interacting with NASA APIs.

Notes:
    This module provides the base API class for interacting with NASA APIs.
    It contains the `BaseAPI` and `NasaAPIException` classes,
        which are used as a foundation for the other packages in the `nasa_apis_wrapper` package.
"""

from typing import Optional

from requests import Session


class NasaAPIException(Exception):
    """
    Represents an exception that occurs when interacting with NASA APIs.

    Attributes:
        message (str): The error message.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BaseAPI:
    """
    Provides a basic implementation for interacting with NASA APIs.

    Attributes:
        host (str): The base URL for the NASA API.
        session (Session): A requests Session object for making API requests.

    Methods:
        __init__: Initializes the BaseAPI object with an API key.
        get_request: Sends a GET request to the NASA API.
        post_request: Sends a POST request to the NASA API.
    """

    def __init__(self, api_key: str):
        """
        Initializes the BaseAPI object with an API key.

        Args:
            api_key (str): The API key for authenticating with the NASA API.

        Notes:
            Sets the host URL and initializes a requests Session object with the API key.
        """
        self.host: str = "https://api.nasa.gov"
        self.session: Session = Session()
        headers: dict = {"Accept": "application/json"}
        self.session.headers.update(headers)
        self.session.params = {"api_key": api_key}

    def get_request(self, endpoint: str, params: Optional[dict] = None):
        """
        Sends a GET request to the NASA API.

        Args:
            endpoint (str): The endpoint for the API request.
            params (Optional[dict]): Additional query parameters for the request.

        Returns:
            Response: The response from the API request.

        Notes:
            Constructs the full URL for the request and sends a
            GET request using the requests Session object.
        """
        url: str = f"{self.host}{endpoint}"
        req = self.session.get(url, params=params)
        if req.status_code not in list(range(200, 300)):
            raise NasaAPIException(req.text)
        return req.text

    def post_request(self, endpoint: str, json_data: dict):
        """
        Sends a POST request to the NASA API.

        Args:
            endpoint (str): The endpoint for the API request.
            json_data (dict): The JSON data to be sent in the request body.

        Returns:
            Response: The response from the API request.

        Notes:
            Constructs the full URL for the request and sends a
            POST request using the requests Session object.
        """
        url: str = f"{self.host}{endpoint}"
        req = self.session.post(url, json=json_data)
        if req.status_code not in list(range(200, 300)):
            raise NasaAPIException(req.text)
        return req.text
