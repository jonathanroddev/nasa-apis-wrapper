import json
from nasa_apis_wrapper import BaseAPI
from .models import APOD


class APODService(BaseAPI):

    def get_astronomy_picture_of_day(self) -> APOD:
        endpoint: str = "/planetary/apod"
        req = self.get_request(endpoint)
        response: dict = json.loads(req.text)
        return APOD(**response)
