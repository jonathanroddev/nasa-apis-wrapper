"""
Initialization file for the APOD module.

This file is used to initialize the module and make its contents available for import.

Attributes:
    APOD: A class representing an Astronomy Picture of the Day (APOD) object.
    APODService: A class providing methods for retrieving APOD data.

Notes:
    This file is automatically executed when the module is imported.
"""

from .models import APOD
from .service import APODService
