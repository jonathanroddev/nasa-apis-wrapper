from requests import Session

class BaseAPI:
    def __init__(self, api_key: str):
        self.host: str = "https://api.nasa.gov"

        headers: dict = {"Accept": "application/json"}

        self.session: Session = Session()
        self.session.headers.update(headers)
        self.session.params = {"api_key": api_key}

    def get_request(self, endpoint: str):
        url: str = f"{self.host}{endpoint}"
        req = self.session.get(url)
        return req