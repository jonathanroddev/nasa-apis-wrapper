# TODO: add docstrings

import json
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
)
from ..utils import Utils


class DonkiService(BaseAPI):
    endpoint_prefix: str = "/DONKI"

    def cme(
        self, generic_donki_request: Optional[GenericDonkiRequest] = None
    ) -> List[DonkiCMEResponse]:
        """
        Coronal Mass Ejection (CME)
        """
        endpoint: str = f"{self.endpoint_prefix}/CME"
        req = self.get_request(
            endpoint,
            params=(
                Utils.obj_dict(generic_donki_request) if generic_donki_request else None
            ),
        )
        response: dict = json.loads(req)
        donki_cme_response_list: List[DonkiCMEResponse] = []
        for _, item in enumerate(response):
            donki_cme_response_list.append(DonkiCMEResponse(**item))
        return donki_cme_response_list

    def cme_analyisis(
        self, donki_cme_analysis_request: Optional[DonkiCMEAnalysisRequest] = None
    ) -> List[CMEAnalysis]:
        """
        Coronal Mass Ejection Analysis (CME Analysis)
        """
        endpoint: str = f"{self.endpoint_prefix}/CMEAnalysis"
        req = self.get_request(
            endpoint,
            params=(
                Utils.obj_dict(donki_cme_analysis_request)
                if donki_cme_analysis_request
                else None
            ),
        )
        response: dict = json.loads(req)
        donki_cme_analysis_response_list: List[CMEAnalysis] = []
        for _, item in enumerate(response):
            donki_cme_analysis_response_list.append(CMEAnalysis(**item))
        return donki_cme_analysis_response_list

    def gst(
        self, generic_donki_request: Optional[GenericDonkiRequest] = None
    ) -> List[DonkiGSTResponse]:
        """
        Geomagnetic Storm (GST)
        """
        endpoint: str = f"{self.endpoint_prefix}/GST"
        req = self.get_request(
            endpoint,
            params=(
                Utils.obj_dict(generic_donki_request) if generic_donki_request else None
            ),
        )
        response: dict = json.loads(req)
        donki_gst_response_list: List[DonkiGSTResponse] = []
        for _, item in enumerate(response):
            donki_gst_response_list.append(DonkiGSTResponse(**item))
        return donki_gst_response_list

    def ips(
        self, donki_ips_request: Optional[DonkiIPSRequest] = None
    ) -> List[DonkiIPSResponse]:
        """
        Interplanetary Shock (IPS)
        """
        endpoint: str = f"{self.endpoint_prefix}/IPS"
        req = self.get_request(
            endpoint,
            params=Utils.obj_dict(donki_ips_request) if donki_ips_request else None,
        )
        response: dict = json.loads(req)
        donki_ips_response_list: List[DonkiIPSResponse] = []
        for _, item in enumerate(response):
            donki_ips_response_list.append(DonkiIPSResponse(**item))
        return donki_ips_response_list

    def flr(
        self, generic_donki_request: Optional[GenericDonkiRequest] = None
    ) -> List[DonkiFLRResponse]:
        """
        Solar Flare (FLR)
        """
        endpoint: str = f"{self.endpoint_prefix}/FLR"
        req = self.get_request(
            endpoint,
            params=(
                Utils.obj_dict(generic_donki_request) if generic_donki_request else None
            ),
        )
        response: dict = json.loads(req)
        donki_flr_response_list: List[DonkiFLRResponse] = []
        for _, item in enumerate(response):
            donki_flr_response_list.append(DonkiFLRResponse(**item))
        return donki_flr_response_list

    def sep(
        self, generic_donki_request: Optional[GenericDonkiRequest] = None
    ) -> List[DonkiSEPResponse]:
        """
        Solar Energetic Particle (SEP)
        """
        endpoint: str = f"{self.endpoint_prefix}/SEP"
        req = self.get_request(
            endpoint,
            params=(
                Utils.obj_dict(generic_donki_request) if generic_donki_request else None
            ),
        )
        response: dict = json.loads(req)
        donki_sep_response_list: List[DonkiSEPResponse] = []
        for _, item in enumerate(response):
            donki_sep_response_list.append(DonkiSEPResponse(**item))
        return donki_sep_response_list

    def mpc(
        self, generic_donki_request: Optional[GenericDonkiRequest] = None
    ) -> List[DonkiMPCResponse]:
        """
        Magnetopause Crossing (MPC)
        """
        endpoint: str = f"{self.endpoint_prefix}/MPC"
        req = self.get_request(
            endpoint,
            params=(
                Utils.obj_dict(generic_donki_request) if generic_donki_request else None
            ),
        )
        response: dict = json.loads(req)
        donki_mpc_response_list: List[DonkiMPCResponse] = []
        for _, item in enumerate(response):
            donki_mpc_response_list.append(DonkiMPCResponse(**item))
        return donki_mpc_response_list

    def rbe(
        self, generic_donki_request: Optional[GenericDonkiRequest] = None
    ) -> List[DonkiRBEResponse]:
        """
        Radiation Belt Enhancement (RBE)
        """
        endpoint: str = f"{self.endpoint_prefix}/RBE"
        req = self.get_request(
            endpoint,
            params=(
                Utils.obj_dict(generic_donki_request) if generic_donki_request else None
            ),
        )
        response: dict = json.loads(req)
        donki_rbe_response_list: List[DonkiRBEResponse] = []
        for _, item in enumerate(response):
            donki_rbe_response_list.append(DonkiRBEResponse(**item))
        return donki_rbe_response_list
