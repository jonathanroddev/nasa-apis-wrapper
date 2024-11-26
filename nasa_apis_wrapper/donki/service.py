# TODO: add docstrings

import json
from typing import Optional, List

from nasa_apis_wrapper.base import BaseAPI
from .models import DonkiRequest, DonkiCMEResponse
from ..utils import Utils


class DonkiService(BaseAPI):
    endpoint_prefix: str = "/DONKI"

    def cme(self, donki_request: Optional[DonkiRequest] = None) -> List[DonkiCMEResponse]:
        """
        Coronal Mass Ejection (CME)
        """
        endpoint: str = f"{self.endpoint_prefix}/CME"
        req = self.get_request(endpoint, params=Utils.obj_dict(donki_request) if donki_request else None)
        response: dict = json.loads(req)
        donki_cme_response_list: List[DonkiCMEResponse] = []
        for _, item in enumerate(response):
            donki_cme_response_list.append(DonkiCMEResponse(**item))
        return donki_cme_response_list
