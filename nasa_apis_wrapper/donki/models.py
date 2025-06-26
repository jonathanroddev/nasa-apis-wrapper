# TODO: add docstrings

import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel


class GenericDonkiRequest(BaseModel):
    startDate: Optional[datetime.date] = None
    endDate: Optional[datetime.date] = None


class DonkiIPSRequest(GenericDonkiRequest):
    location: Optional[Literal["Earth", "MESSENGER", "STEREO A", "STEREO B"]] = None
    catalog: Optional[Literal["SWRC_CATALOG", "WINSLOW_MESSENGER_ICME_CATALOG"]] = None


class DonkiCMEAnalysisRequest(GenericDonkiRequest):
    mostAccurateOnly: Optional[bool] = None
    completeEntryOnly: Optional[bool] = None
    speed: Optional[int] = None
    halfAngle: Optional[int] = None
    catalog: Optional[Literal["ALL", "SWRC_CATALOG", "JANG_ET_AL_CATALOG"]] = None
    keyword: Optional[str] = None


class Instrument(BaseModel):
    displayName: str


class LinkEvent(BaseModel):
    activityID: str


class Impact(BaseModel):
    isGlancingBlow: bool
    location: str
    arrivalTime: str


class EnlilCommonResponse(BaseModel):
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


class Enlil(EnlilCommonResponse):
    cmeIDs: List[str]


class CMECommonResponse(BaseModel):
    latitude: float
    longitude: Optional[float] = None
    speed: float
    time21_5: str
    halfAngle: float
    featureCode: str
    isMostAccurate: bool
    levelOfData: Optional[int] = None


class CMEAnalysis(CMECommonResponse):
    type: str
    imageType: Optional[str] = None
    measurementTechnique: str
    note: str
    tilt: Optional[str] = None
    minorHalfWidth: Optional[str] = None
    speedMeasuredAtHeight: Optional[float] = None
    submissionTime: str
    link: str
    enlilList: Optional[List[Enlil]] = None
    associatedCMEID: Optional[str] = None
    catalog: Optional[str] = None
    dataLevel: Optional[str] = None
    versionId: Optional[int] = None


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


class KpIndexItem(BaseModel):
    observedTime: str
    kpIndex: float
    source: str


class DonkiGSTResponse(BaseModel):
    gstID: str
    startTime: str
    allKpIndex: List[KpIndexItem]
    link: str
    linkedEvents: List[LinkEvent]
    submissionTime: str
    versionId: int


class DonkiGenericResponse(BaseModel):
    instruments: List[Instrument]
    submissionTime: Optional[str]
    versionId: int
    link: Optional[str]


class DonkiGenericEventTimeResponse(DonkiGenericResponse):
    eventTime: str


class DonkiIPSResponse(DonkiGenericEventTimeResponse):
    activityID: str
    catalog: Optional[str]
    location: str


class DonkiGenericFullResponse(DonkiGenericEventTimeResponse):
    linkedEvents: List[LinkEvent]


class DonkiFLRResponse(DonkiGenericResponse):
    flrID: str
    catalog: str
    beginTime: str
    peakTime: str
    endTime: Optional[str]
    classType: str
    sourceLocation: str
    activeRegionNum: int
    note: str
    linkedEvents: Optional[List[LinkEvent]]


class DonkiSEPResponse(DonkiGenericFullResponse):
    sepID: str


class DonkiMPCResponse(DonkiGenericFullResponse):
    mpcID: str


class DonkiRBEResponse(DonkiGenericFullResponse):
    rbeID: str


class DonkiHSSResponse(DonkiGenericEventTimeResponse):
    hssID: str
    linkedEvents: Optional[List[LinkEvent]]


class CMEInput(CMECommonResponse):
    cmeStartTime: str
    ipsList: Optional[List[DonkiIPSResponse]] = []
    cmeid: str


class DonkiWSAEnlilSimulationResponse(EnlilCommonResponse):
    simulationID: str
    cmeInputs: List[CMEInput]
