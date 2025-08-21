# main.py
import asyncio
import uvloop
from typing import Any, Dict
from config import Config
from storage import (
    read_last_event_id,
    save_last_event_id,
)
from usgs_api import USGSEarthquakeAPI
from telegram import TelegramBot
from logger import logger
from geopy.distance import geodesic
from mapgen import generate_cartopy_map


def format_message(props, coords, quake_time, distance_km) -> str:
    lon, lat, depth = coords
    mag = props.get("mag", "N/A")
    mag_type = props.get("magType", "N/A")
    place = props.get("place", "Unknown location")
    alert = props.get("alert", "N/A")
    tsunami = "มีความเสี่ยง" if props.get("tsunami", 0) == 1 else "ไม่มี"
    cdi = props.get("cdi", "N/A")
    mmi = props.get("mmi", "N/A")
    url = props.get("url", "N/A")
    net = props.get("net", "N/A")
    sources = props.get("sources", "N/A")

    return f"""
        📌 <b>แผ่นดินไหวใกล้: {place}</b>
        📏 <b>ห่างจากกรุงเทพฯประมาณ:</b> {distance_km:.2f} กม.
        🕒 <b>เวลา:</b> {quake_time}
        🌍 <b>ขนาด:</b> M{mag} ({mag_type})
        📉 <b>ความลึก:</b> {depth} กม.
        📈 <b>ระดับแรงสั่น:</b> CDI: {cdi}, MMI: {mmi}

        🚨 <b>ระดับการแจ้งเตือน (PAGER):</b> {alert}
        🌊 <b>สึนามิ:</b> {tsunami}

        📡 <b>เครือข่าย:</b> {net}
        🛰️ <b>แหล่งข้อมูล:</b> {sources}
        🔎 <b>ข้อมูลเพิ่มเติม:</b> <a href="{url}">ดูรายละเอียดจาก USGS</a>
        """


async def handle_new_earthquake(
    api: USGSEarthquakeAPI, bot: TelegramBot, quake: Dict[str, Any]
) -> None:
    event_id = quake["id"]
    props = quake["properties"]
    coords = quake["geometry"]["coordinates"]
    quake_lat, quake_lon = coords[1], coords[0]
    place = props.get("place", "Unknown location")
    quake_time = api.format_quake_time(props["time"])

    logger.info(f"Processing earthquake event ID: {event_id}")
    logger.info(f"Coordinates: latitude={quake_lat}, longitude={quake_lon}")
    logger.info(f"Location description: {place}")
    logger.info(f"Event time (local): {quake_time}")

    # Calculate distance
    distance_km = geodesic(
        (Config.BANGKOK_LAT, Config.BANGKOK_LON), (quake_lat, quake_lon)
    ).km
    logger.info(f"Distance from Bangkok: {distance_km:.2f} km")

    if distance_km > 2500:
        logger.info(
            f"Event is outside the 2500 km radius ({distance_km:.2f} km). Notification skipped."
        )
        return

    # Format and send alert
    logger.info(
        f"Sending notification for earthquake near: {place} ({distance_km:.2f} km from Bangkok)"
    )
    # Offload blocking map generation to a thread
    image_path = await asyncio.to_thread(
        generate_cartopy_map, quake_lat, quake_lon, place, distance_km
    )
    await bot.send_photo(image_path)
    await bot.send_message(format_message(props, coords, quake_time, distance_km))
    save_last_event_id(event_id)
    logger.info(f"Event ID {event_id} saved to notified events.")


async def monitor_loop():
    bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
    logger.info("Using TELEGRAM_CHAT_ID from environment.")

    api = USGSEarthquakeAPI()
    notified_event_ids = read_last_event_id()
    try:
        while True:
            try:
                logger.info("Polling USGS Earthquake API for recent events...")
                result = await api.query(minmagnitude=4, orderby="time", limit=10)
                if result.get("features"):
                    logger.info(
                        f"{len(result['features'])} earthquake events received."
                    )
                    for quake in result["features"]:
                        event_id = quake["id"]

                        if event_id in notified_event_ids:
                            logger.info(
                                f"Event ID {event_id} has already been processed. Skipping."
                            )
                            continue
                        await handle_new_earthquake(api, bot, quake)
                        notified_event_ids.add(event_id)
                else:
                    logger.warning("No earthquake events found in API response.")

            except Exception as e:
                logger.error(
                    "An exception occurred during earthquake monitoring loop.",
                    exc_info=True,
                )

            logger.info(
                f"Sleeping for {Config.FETCH_INTERVAL_SECONDS} seconds before next poll."
            )
            await asyncio.sleep(Config.FETCH_INTERVAL_SECONDS)
    finally:
        await bot.aclose()
        await api.aclose()


if __name__ == "__main__":
    logger.info("USGS Earthquake Monitoring Service started.")
    uvloop.install()
    asyncio.run(monitor_loop())
