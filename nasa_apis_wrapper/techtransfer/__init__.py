from .models import (
    PatentResult,
    PatentResponse,
    SoftwareResult,
    SoftwareResponse,
    SpinoffResult,
    SpinoffResponse,
    TechTransferItem,
    TechTransferSearchResponse,
)
from .service import TechTransferService

__all__ = [
    "TechTransferService",
    "PatentResult",
    "PatentResponse",
    "SoftwareResult",
    "SoftwareResponse",
    "SpinoffResult",
    "SpinoffResponse",
    "TechTransferItem",
    "TechTransferSearchResponse",
]
