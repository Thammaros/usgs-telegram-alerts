# usgs_api.py
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, List, Literal, TypedDict
from config import Config
from logger import logger


# TypedDict definitions for USGS GeoJSON response
class Properties(TypedDict, total=False):
    mag: float
    magType: str
    place: str
    time: int
    alert: str
    tsunami: int
    cdi: float
    mmi: float
    url: str
    net: str
    sources: str


class Geometry(TypedDict):
    type: Literal["Point"]
    coordinates: List[float]  # [lon, lat, depth_km]


class Feature(TypedDict):
    id: str
    properties: Properties
    geometry: Geometry


class FeatureCollection(TypedDict):
    type: Literal["FeatureCollection"]
    features: List[Feature]


class USGSEarthquakeAPI:
    BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/"

    def __init__(self):
        self.session = httpx.Client(http2=True, timeout=10)
        self.timezone = ZoneInfo(Config.TIMEZONE)

    def query(self, **params: Any) -> FeatureCollection:
        params.setdefault("format", "geojson")
        url = f"{self.BASE_URL}query"

        try:
            response = self.session.get(url, params=params)
            self._handle_response(response)
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"❌ HTTP error: {e.response.status_code} - {e.response.reason_phrase}"
            )
            raise

        except httpx.ConnectError as e:
            logger.error("❌ Connection error: Could not reach USGS API.")
            raise

        except httpx.ReadTimeout as e:
            logger.error("⏱️ Request to USGS API timed out.")
            raise

        except httpx.RequestError as e:
            logger.error(f"❌ Unexpected error during API request: {e}")
            raise

    def format_quake_time(self, quake_time_ms: int) -> str:
        dt_utc = datetime.fromtimestamp(quake_time_ms / 1000, tz=ZoneInfo("UTC"))
        return dt_utc.astimezone(self.timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    def _handle_response(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
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
