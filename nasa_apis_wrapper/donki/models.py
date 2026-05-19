import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class GenericDonkiRequest(BaseModel):
    """Base request with optional date range, shared by most DONKI endpoints."""
    startDate: Optional[datetime.date] = None
    endDate: Optional[datetime.date] = None


class DonkiIPSRequest(GenericDonkiRequest):
    """Request model for the Interplanetary Shock (IPS) endpoint."""
    location: Optional[Literal["Earth", "MESSENGER", "STEREO A", "STEREO B"]] = None
    catalog: Optional[Literal["M2M_CATALOG", "WINSLOW_MESSENGER_ICME_CATALOG"]] = None


class DonkiCMEAnalysisRequest(GenericDonkiRequest):
    """Request model for the CME Analysis endpoint."""
    mostAccurateOnly: Optional[bool] = None
    completeEntryOnly: Optional[bool] = None
    speed: Optional[int] = None
    halfAngle: Optional[int] = None
    catalog: Optional[Literal["ALL", "SWRC_CATALOG", "JANG_ET_AL_CATALOG"]] = None
    keyword: Optional[str] = None


class DonkiNotificationsRequest(GenericDonkiRequest):
    """Request model for the Notifications endpoint."""
    type: Optional[
        Literal["all", "FLR", "SEP", "CME", "IPS", "MPC", "GST", "RBE", "report"]
    ] = None


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class Instrument(BaseModel):
    displayName: str


class LinkEvent(BaseModel):
    activityID: str


class Impact(BaseModel):
    isGlancingBlow: bool
    location: str
    arrivalTime: str


# ---------------------------------------------------------------------------
# Enlil / WSA-Enlil
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# CME
# ---------------------------------------------------------------------------

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
    cmeAnalyses: List[CMEAnalysis] = []
    linkedEvents: Optional[List[LinkEvent]] = None


# ---------------------------------------------------------------------------
# GST
# ---------------------------------------------------------------------------

class KpIndexItem(BaseModel):
    observedTime: str
    kpIndex: float
    source: str


class DonkiGSTResponse(BaseModel):
    gstID: str
    startTime: str
    allKpIndex: List[KpIndexItem]
    link: str
    linkedEvents: Optional[List[LinkEvent]] = None
    submissionTime: str
    versionId: int


# ---------------------------------------------------------------------------
# Shared base response models
# ---------------------------------------------------------------------------

class DonkiGenericResponse(BaseModel):
    """Base response shared by IPS, SEP, MPC, RBE, HSS."""
    instruments: List[Instrument]
    submissionTime: Optional[str] = None
    versionId: int
    link: Optional[str] = None


class DonkiGenericEventTimeResponse(DonkiGenericResponse):
    eventTime: str


# ---------------------------------------------------------------------------
# IPS
# ---------------------------------------------------------------------------

class DonkiIPSResponse(DonkiGenericEventTimeResponse):
    activityID: str
    catalog: Optional[str] = None
    location: str


# ---------------------------------------------------------------------------
# FLR, SEP, MPC, RBE
# ---------------------------------------------------------------------------

class DonkiGenericFullResponse(DonkiGenericEventTimeResponse):
    linkedEvents: Optional[List[LinkEvent]] = None


class DonkiFLRResponse(DonkiGenericResponse):
    flrID: str
    catalog: str
    beginTime: str
    peakTime: str
    endTime: Optional[str] = None
    classType: str
    sourceLocation: str
    activeRegionNum: Optional[int] = None
    note: str
    linkedEvents: Optional[List[LinkEvent]] = None


class DonkiSEPResponse(DonkiGenericFullResponse):
    sepID: str


class DonkiMPCResponse(DonkiGenericFullResponse):
    mpcID: str


class DonkiRBEResponse(DonkiGenericFullResponse):
    rbeID: str


# ---------------------------------------------------------------------------
# HSS
# ---------------------------------------------------------------------------

class DonkiHSSResponse(DonkiGenericEventTimeResponse):
    hssID: str
    linkedEvents: Optional[List[LinkEvent]] = None


# ---------------------------------------------------------------------------
# WSA-Enlil simulation
# ---------------------------------------------------------------------------

class CMEInput(CMECommonResponse):
    cmeStartTime: str
    ipsList: Optional[List[DonkiIPSResponse]] = []
    cmeid: str


class DonkiWSAEnlilSimulationResponse(EnlilCommonResponse):
    simulationID: str
    cmeInputs: List[CMEInput]


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class DonkiNotificationResponse(BaseModel):
    messageType: str
    messageID: str
    messageURL: str
    messageIssueTime: str
    messageBody: str
