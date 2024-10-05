"""
Module for Astronomy Picture of the Day (APOD) service.

This module contains the APODService class, which provides methods for retrieving APOD data.

Classes:
    APODService: Provides methods for retrieving APOD data.
"""

import json

from nasa_apis_wrapper.base import BaseAPI
from .models import APOD


class APODService(BaseAPI):
    """
        Provides methods for retrieving APOD data.

        Attributes:
            None

        Methods:
            get_astronomy_picture_of_day: Retrieves the APOD for the current day.
        """

    def get_astronomy_picture_of_day(self) -> APOD:
        """
            Retrieves the APOD for the current day.

            Returns:
                APOD: The APOD object for the current day.

            Notes:
                This method sends a GET request to the NASA APOD API to retrieve the APOD data.
            """
        endpoint: str = "/planetary/apod"
        req = self.get_request(endpoint)
        response: dict = json.loads(req.text)
        return APOD(**response)
