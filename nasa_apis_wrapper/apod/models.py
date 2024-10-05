"""
Module for Astronomy Picture of the Day (APOD) data models.

This module contains the APOD class, which represents an Astronomy Picture of the Day object.
It provides attributes for the APOD's copyright information, date, explanation, high-definition URL,
media type, and URL.

Classes:
    APOD: Represents an Astronomy Picture of the Day object.
"""

import datetime
from typing import Optional

from pydantic import BaseModel


class APOD(BaseModel):
    """
       Represents an Astronomy Picture of the Day (APOD) object.

       Attributes:
           copyright (Optional[str]): The copyright information for the APOD image.
           date (datetime.date): The date the APOD was published.
           explanation (str): A brief explanation of the APOD image.
           hdurl (Optional[str]): The URL of the high-definition version of the APOD image.
           media_type (str): The type of media (e.g., image, video) for the APOD.
           url (str): The URL of the APOD image.
       """
    copyright: Optional[str] = None
    date: datetime.date
    explanation: str
    hdurl: Optional[str] = None
    media_type: str
    url: str
