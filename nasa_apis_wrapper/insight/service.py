from nasa_apis_wrapper.base import BaseAPI
from .models import InsightWeatherResponse


class InsightService(BaseAPI):
    """
    Service for the NASA InSight Mars Weather Service API.

    Provides access to meteorological data recorded by the InSight lander
    at Elysium Planitia, Mars. Sensors covered:

    - **AT** — Atmospheric temperature (°C), via TWINS instrument
    - **HWS** — Horizontal wind speed (m/s), via TWINS
    - **PRE** — Atmospheric pressure (Pa), via APSS/PS
    - **WD** — Wind direction (16-point compass rose), via TWINS

    .. warning::
        The InSight mission ended on 21 December 2022 due to dust accumulation
        on its solar panels. This endpoint still responds but always returns the
        same frozen dataset from October 2020 (Sols 675–681). It is included
        for completeness and archival use.
    """

    def weather(self) -> InsightWeatherResponse:
        """
        Retrieve the 7 most recent Sols of Mars weather data.

        Returns:
            InsightWeatherResponse containing per-Sol atmospheric readings
            and data validity metadata.

        Raises:
            NasaAPIException: If the API request fails.
        """
        data = self.get_request(
            "/insight_weather/",
            params={"feedtype": "json", "ver": "1.0"},
        )
        return InsightWeatherResponse(**data)
