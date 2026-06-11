"""
Initialization file for the Base API module.

This file is used to initialize the module and make its contents available for import.

Classes:
    BaseAPI: Provides a basic implementation for interacting with NASA APIs.
    NasaAPIException: Represents an exception that occurs when interacting with NASA APIs.

Notes:
    This module provides the base classes and utilities for the `nasa_apis_wrapper` package.
    It contains the `BaseAPI` and `NasaAPIException` classes,
        which are used as a foundation for the other packages in the `nasa_apis_wrapper` package.
"""

from .api import BaseAPI, NasaAPIException

__all__ = [
    "BaseAPI",
    "NasaAPIException",
]
