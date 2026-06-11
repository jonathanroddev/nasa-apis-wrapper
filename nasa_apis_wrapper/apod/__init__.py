"""
Initialization file for the APOD module.

This file is used to initialize the module and make its contents available for import.

Attributes:
    APOD: A class representing an Astronomy Picture of the Day (APOD) object.
    APODRequest: A class for initializing a request object for Astronomy Picture of the Day (APOD) data.
    APODService: A class providing methods for retrieving APOD data.

Notes:
    This file is automatically executed when the module is imported.
"""

from .models import APOD, APODRequest
from .service import APODService

__all__ = [
    "APOD",
    "APODRequest",
    "APODService",
]
