"""
Module for utility functions.

This module contains a collection of utility functions
    that can be used throughout the NASA APIs wrapper.
"""
import datetime
from typing import Any


class Utils:
    """
    A class providing utility functions.

    This class contains a collection of utility functions
        that can be used throughout the NASA APIs wrapper.
    """

    @staticmethod
    def obj_dict(obj: Any):
        """
        Converts an object into a dictionary.

        Args:
            obj: The object to be converted into a dictionary.

        Returns:
            A dictionary representation of the object.
        """
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y/%m/%d")
        return obj.__dict__
