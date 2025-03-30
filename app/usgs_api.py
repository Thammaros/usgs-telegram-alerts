import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict
from config import Config
from logger import logger


class USGSEarthquakeAPI:
    BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/"

    def __init__(self):
        self.session = requests.Session()
        self.timezone = ZoneInfo(Config.TIMEZONE)

    def query(self, **params: Any) -> Dict:
        params.setdefault("format", "geojson")
        url = f"{self.BASE_URL}query"

        try:
            response = self.session.get(url, params=params, timeout=10)
            self._handle_response(response)
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"❌ HTTP error: {e.response.status_code} - {e.response.reason}"
            )
            raise

        except requests.exceptions.ConnectionError as e:
            logger.error("❌ Connection error: Could not reach USGS API.")
            raise

        except requests.exceptions.Timeout as e:
            logger.error("⏱️ Request to USGS API timed out.")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Unexpected error during API request: {e}")
            raise

    def format_quake_time(self, quake_time_ms: int) -> str:
        dt_utc = datetime.fromtimestamp(quake_time_ms / 1000, tz=ZoneInfo("UTC"))
        return dt_utc.astimezone(self.timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    def _handle_response(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status = response.status_code
            if status == 400:
                raise ValueError("Bad request: Check your parameters.") from e
            elif status == 404:
                raise ValueError(
                    "Not found: No earthquake data for the given query."
                ) from e
            elif status == 429:
                raise ValueError(
                    "Too many requests: You are being rate limited by the USGS API."
                ) from e
            elif 500 <= status < 600:
                raise ValueError(
                    "Server error: USGS service is temporarily unavailable."
                ) from e
            else:
                raise
