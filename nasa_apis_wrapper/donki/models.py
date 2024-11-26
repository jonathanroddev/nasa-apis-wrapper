# TODO: add docstrings

import datetime
from typing import Optional, List

from pydantic import BaseModel


class DonkiRequest(BaseModel):
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None


class Instrument(BaseModel):
    displayName: str


class LinkEvent(BaseModel):
    activityID: str


class Impact(BaseModel):
    isGlancingBlow: bool
    location: str
    arrivalTime: str


class Enlil(BaseModel):
    modelCompletionTime: str
    au: float
    estimatedShockArrivalTime: Optional[str] = None
    estimatedDuration: Optional[float] = None
    rmin_re: Optional[float] = None
    kp_18: Optional[int] = None
    kp_90: Optional[int] = None
    kp_135: Optional[int] = None
    kp_180: Optional[int] = None
    isEarthGB: bool
    link: str
    impactList: Optional[List[Impact]] = None
    cmeIDs: List[str]


class CMEAnalysis(BaseModel):
    isMostAccurate: bool
    time21_5: str
    latitude: float
    longitude: Optional[float] = None
    halfAngle: float
    speed: float
    type: str
    featureCode: str
    imageType: Optional[str] = None
    measurementTechnique: str
    note: str
    levelOfData: int
    tilt: Optional[str] = None
    minorHalfWidth: Optional[str] = None
    speedMeasuredAtHeight: Optional[float] = None
    submissionTime: str
    link: str
    enlilList: Optional[List[Enlil]] = None


class DonkiCMEResponse(BaseModel):
    activityID: str
    catalog: str
    startTime: str
    instruments: List[Instrument]
    sourceLocation: str
    activeRegionNum: Optional[int] = None
    note: str
    submissionTime: str
    versionId: int
    link: str
    cmeAnalyses: List[CMEAnalysis]
    linkedEvents: Optional[List[LinkEvent]] = None
