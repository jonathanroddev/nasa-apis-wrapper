"""
Module for utility functions.

This module contains a collection of utility functions
    that can be used throughout the NASA APIs wrapper.
"""

from pydantic import BaseModel


class Utils:
    """
    A class providing utility functions.

    This class contains a collection of utility functions
        that can be used throughout the NASA APIs wrapper.
    """

    @staticmethod
    def obj_dict(obj: BaseModel) -> dict:
        """
        Converts a Pydantic model into a query-params dictionary, excluding None fields.

        Args:
            obj: The Pydantic model to be converted.

        Returns:
            A dictionary with non-None fields only.
        """
        return obj.model_dump(exclude_none=True)
