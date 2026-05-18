"""
Initialization file for the donki module.

This file initializes the submodule and makes its contents available for import.

Classes:
    GenericDonkiRequest: Base request model for DONKI API.
    DonkiCMEResponse: Response model for CME events.
    DonkiCMEAnalysisRequest: Request model for CME analysis.
    CMEAnalysis: Model for CME analysis data.
    DonkiGSTResponse: Response model for GST events.
    DonkiIPSRequest: Request model for IPS events.
    DonkiIPSResponse: Response model for IPS events.
    DonkiFLRResponse: Response model for FLR events.
    DonkiSEPResponse: Response model for SEP events.
    DonkiMPCResponse: Response model for MPC events.
    DonkiRBEResponse: Response model for RBE events.
    DonkiHSSResponse: Response model for HSS events.
    DonkiWSAEnlilSimulationResponse: Response model for WSA-Enlil simulations.
    DonkiNotificationsRequest: Request model for notifications.
    DonkiNotificationResponse: Response model for notifications.

Services:
    DonkiService: Provides methods to interact with NASA's DONKI API.

Notes:
    This submodule provides the main models and services for interacting with NASA's DONKI API.
    It serves as the foundation for managing solar event data within the `nasa_apis_wrapper` package.
"""

from .models import (
    GenericDonkiRequest,
    DonkiCMEResponse,
    DonkiCMEAnalysisRequest,
    CMEAnalysis,
    DonkiGSTResponse,
    DonkiIPSRequest,
    DonkiIPSResponse,
    DonkiFLRResponse,
    DonkiSEPResponse,
    DonkiMPCResponse,
    DonkiRBEResponse,
    DonkiHSSResponse,
    DonkiWSAEnlilSimulationResponse,
    DonkiNotificationsRequest,
    DonkiNotificationResponse,
)
from .service import DonkiService

__all__ = [
    "DonkiService",
    "GenericDonkiRequest",
    "DonkiCMEResponse",
    "DonkiCMEAnalysisRequest",
    "CMEAnalysis",
    "DonkiGSTResponse",
    "DonkiIPSRequest",
    "DonkiIPSResponse",
    "DonkiFLRResponse",
    "DonkiSEPResponse",
    "DonkiMPCResponse",
    "DonkiRBEResponse",
    "DonkiHSSResponse",
    "DonkiWSAEnlilSimulationResponse",
    "DonkiNotificationsRequest",
    "DonkiNotificationResponse",
]
