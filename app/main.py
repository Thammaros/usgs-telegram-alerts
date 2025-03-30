import time
from config import Config
from storage import (
    read_last_event_id,
    save_last_event_id,
)
from usgs_api import USGSEarthquakeAPI
from telegram import TelegramBot
from logger import logger
from math import radians, cos, sin, asin, sqrt
from mapgen import generate_cartopy_map


def calculate_distance_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    return round(R * c, 2)


def format_message(props, coords, quake_time, distance_km) -> str:
    lon, lat, depth = coords
    mag = props.get("mag", "N/A")
    mag_type = props.get("magType", "N/A")
    place = props.get("place", "Unknown location")
    event_type = props.get("type", "unknown")
    status = props.get("status", "unknown")
    tsunami = "🌊 Yes" if props.get("tsunami", 0) == 1 else "No"
    alert = props.get("alert", "None")
    felt = props.get("felt", "N/A")
    cdi = props.get("cdi", "N/A")
    mmi = props.get("mmi", "N/A")
    sig = props.get("sig", "N/A")
    gap = props.get("gap", "N/A")
    url = props.get("url", "N/A")
    products = ", ".join(props.get("types", "").split(","))
    net = props.get("net", "N/A")
    code = props.get("code", "N/A")
    ids = props.get("ids", "N/A")
    sources = props.get("sources", "N/A")
    dmin = props.get("dmin", "N/A")
    rms = props.get("rms", "N/A")
    nst = props.get("nst", "N/A")

    return f"""
📍 ตำแหน่ง: {place}
📏 ระยะทางจากกรุงเทพฯ: {distance_km} กม.
📅 เวลาในท้องถิ่น: {quake_time}
💥 ขนาดแผ่นดินไหว: M{mag} ({mag_type}) - {"W-phase" if mag_type == "mww" else "Body-wave"}
📏 ความลึก: {depth} กม.
🌀 ประเภทเหตุการณ์: {event_type}
✅ สถานะ: {status}
🌊 การแจ้งเตือนสึนามิ: {tsunami}
🚨 ระดับการเตือนภัย (PAGER): {alert}
👥 รายงานความรู้สึก: {felt} คน
📈 CDI (ระดับการสั่นที่รู้สึกได้): {cdi} | 📉 MMI (ระดับแรงสั่นสะเทือน): {mmi}
🎯 คะแนนความสำคัญ (Significance): {sig}
🧭 ช่องว่างเชิงมุม (Azimuthal Gap): {gap}°
📡 เครือข่ายวัดแผ่นดินไหว: {net}
🌐 แหล่งข้อมูล: {sources}
📍 ระยะทางน้อยที่สุดจากสถานีวัด: {dmin}°
📊 ค่าความคลาดเคลื่อน RMS: {rms} วินาที
📡 จำนวนสถานีที่ใช้: {nst}
🔗 ข้อมูลเพิ่มเติม: {url}
"""


def handle_new_earthquake(
    api: USGSEarthquakeAPI, bot: TelegramBot, quake, last_event_id: str
) -> str:
    event_id = quake["id"]

    if event_id == last_event_id:
        logger.info("No new event.")
        return last_event_id

    props = quake["properties"]
    coords = quake["geometry"]["coordinates"]
    quake_lat, quake_lon = coords[1], coords[0]
    place = props.get("place", "Unknown location")
    quake_time = api.format_quake_time(props["time"])
    distance_km = calculate_distance_km(
        Config.BANGKOK_LAT, Config.BANGKOK_LON, quake_lat, quake_lon
    )

    message = format_message(props, coords, quake_time, distance_km)

    logger.info("New earthquake detected.")
    image_path = generate_cartopy_map(quake_lat, quake_lon, place, distance_km)
    bot.send_photo(image_path)
    bot.send_message(message)
    save_last_event_id(event_id)

    return event_id


def monitor_loop():
    bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
    chat_id = bot.load_or_fetch_chat_id()

    if not chat_id:
        return

    api = USGSEarthquakeAPI()
    last_event_id = read_last_event_id()

    while True:
        try:
            result = api.query(minmagnitude=5, orderby="time", limit=1)

            if result.get("features"):
                quake = result["features"][0]
                last_event_id = handle_new_earthquake(api, bot, quake, last_event_id)
            else:
                logger.warning("No earthquake data found.")

        except Exception as e:
            logger.error(f"Exception occurred: {e}", exc_info=True)

        time.sleep(Config.FETCH_INTERVAL_SECONDS)


if __name__ == "__main__":
    monitor_loop()
