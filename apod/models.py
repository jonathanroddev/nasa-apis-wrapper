from pydantic import BaseModel
from typing import Optional
import datetime

class APOD (BaseModel):
    copyright: Optional[str] = None
    date: datetime.date
    explanation: str
    hdurl: Optional[str] = None
    media_type: str
    url: str