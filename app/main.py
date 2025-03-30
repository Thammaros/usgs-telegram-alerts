import time
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


def handle_new_earthquake(api: USGSEarthquakeAPI, bot: TelegramBot, quake) -> None:
    event_id = quake["id"]

    props = quake["properties"]
    coords = quake["geometry"]["coordinates"]
    quake_lat, quake_lon = coords[1], coords[0]
    place = props.get("place", "Unknown location")
    quake_time = api.format_quake_time(props["time"])

    # Calculate distance
    distance_km = geodesic(
        (Config.BANGKOK_LAT, Config.BANGKOK_LON), (quake_lat, quake_lon)
    ).km

    if distance_km > 2500:
        logger.info(f"🌐 Skipping distant event ({distance_km:.2f} km)")
        return

    # Format and send
    message = format_message(props, coords, quake_time, distance_km)
    logger.info(f"📡 New earthquake within 2500 km: {place} ({distance_km:.2f} km)")
    image_path = generate_cartopy_map(quake_lat, quake_lon, place, distance_km)
    bot.send_photo(image_path)
    bot.send_message(message)
    save_last_event_id(event_id)


def monitor_loop():
    bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
    chat_id = bot.load_or_fetch_chat_id()

    if not chat_id:
        return

    api = USGSEarthquakeAPI()
    notified_event_ids = read_last_event_id()

    while True:
        try:
            result = api.query(minmagnitude=5, orderby="time", limit=10)

            if result.get("features"):
                for quake in result["features"]:
                    event_id = quake["id"]
                    if event_id in notified_event_ids:
                        continue
                    handle_new_earthquake(api, bot, quake)
                    notified_event_ids.add(event_id)
            else:
                logger.warning("No earthquake data found.")

        except Exception as e:
            logger.error(f"Exception occurred: {e}", exc_info=True)

        time.sleep(Config.FETCH_INTERVAL_SECONDS)


if __name__ == "__main__":
    logger.info("Starting USGS Earthquake Monitoring Service...")
    monitor_loop()
