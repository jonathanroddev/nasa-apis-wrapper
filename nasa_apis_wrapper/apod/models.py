import datetime
from typing import Optional
from pydantic import BaseModel


class APOD(BaseModel):
    copyright: Optional[str] = None
    date: datetime.date
    explanation: str
    hdurl: Optional[str] = None
    media_type: str
    url: str
