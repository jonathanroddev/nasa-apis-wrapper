from typing import Optional, List

from nasa_apis_wrapper.base import BaseAPI
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
from ..utils import obj_dict


class DonkiService(BaseAPI):
    """
    Service for the Space Weather Database Of Notifications, Knowledge, Information (DONKI) API.

    Provides access to solar and geomagnetic event data: coronal mass ejections,
    geomagnetic storms, solar flares, radiation belt enhancements, and more.
    """

    endpoint_prefix: str = "/DONKI"

    def cme(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiCMEResponse]:
        """
        Retrieve Coronal Mass Ejection (CME) events.

        Args:
            request: Optional date range filter.

        Returns:
            List of CME events within the requested period.
        """
        return self._parse_list(f"{self.endpoint_prefix}/CME", DonkiCMEResponse, obj_dict(request) if request else None)

    def cme_analysis(self, request: Optional[DonkiCMEAnalysisRequest] = None) -> List[CMEAnalysis]:
        """
        Retrieve Coronal Mass Ejection Analysis records.

        Args:
            request: Optional filters including date range, catalog, speed, and half-angle.

        Returns:
            List of CME analysis entries.
        """
        return self._parse_list(f"{self.endpoint_prefix}/CMEAnalysis", CMEAnalysis, obj_dict(request) if request else None)

    def gst(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiGSTResponse]:
        """
        Retrieve Geomagnetic Storm (GST) events.

        Args:
            request: Optional date range filter.

        Returns:
            List of geomagnetic storm events.
        """
        return self._parse_list(f"{self.endpoint_prefix}/GST", DonkiGSTResponse, obj_dict(request) if request else None)

    def ips(self, request: Optional[DonkiIPSRequest] = None) -> List[DonkiIPSResponse]:
        """
        Retrieve Interplanetary Shock (IPS) events.

        Args:
            request: Optional filters including date range, location, and catalog.

        Returns:
            List of interplanetary shock events.
        """
        return self._parse_list(f"{self.endpoint_prefix}/IPS", DonkiIPSResponse, obj_dict(request) if request else None)

    def flr(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiFLRResponse]:
        """
        Retrieve Solar Flare (FLR) events.

        Args:
            request: Optional date range filter.

        Returns:
            List of solar flare events.
        """
        return self._parse_list(f"{self.endpoint_prefix}/FLR", DonkiFLRResponse, obj_dict(request) if request else None)

    def sep(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiSEPResponse]:
        """
        Retrieve Solar Energetic Particle (SEP) events.

        Args:
            request: Optional date range filter.

        Returns:
            List of solar energetic particle events.
        """
        return self._parse_list(f"{self.endpoint_prefix}/SEP", DonkiSEPResponse, obj_dict(request) if request else None)

    def mpc(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiMPCResponse]:
        """
        Retrieve Magnetopause Crossing (MPC) events.

        Args:
            request: Optional date range filter.

        Returns:
            List of magnetopause crossing events.
        """
        return self._parse_list(f"{self.endpoint_prefix}/MPC", DonkiMPCResponse, obj_dict(request) if request else None)

    def rbe(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiRBEResponse]:
        """
        Retrieve Radiation Belt Enhancement (RBE) events.

        Args:
            request: Optional date range filter.

        Returns:
            List of radiation belt enhancement events.
        """
        return self._parse_list(f"{self.endpoint_prefix}/RBE", DonkiRBEResponse, obj_dict(request) if request else None)

    def hss(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiHSSResponse]:
        """
        Retrieve High Speed Stream (HSS) events.

        Args:
            request: Optional date range filter.

        Returns:
            List of high speed stream events.
        """
        return self._parse_list(f"{self.endpoint_prefix}/HSS", DonkiHSSResponse, obj_dict(request) if request else None)

    def wsa_enlil_simulation(self, request: Optional[GenericDonkiRequest] = None) -> List[DonkiWSAEnlilSimulationResponse]:
        """
        Retrieve WSA+Enlil Solar Wind Prediction simulation results.

        Args:
            request: Optional date range filter.

        Returns:
            List of WSA-Enlil simulation entries.
        """
        return self._parse_list(f"{self.endpoint_prefix}/WSAEnlilSimulations", DonkiWSAEnlilSimulationResponse, obj_dict(request) if request else None)

    def notifications(self, request: Optional[DonkiNotificationsRequest] = None) -> List[DonkiNotificationResponse]:
        """
        Retrieve DONKI space weather notifications.

        Args:
            request: Optional filters including date range and notification type.

        Returns:
            List of space weather notification messages.
        """
        return self._parse_list(f"{self.endpoint_prefix}/notifications", DonkiNotificationResponse, obj_dict(request) if request else None)
