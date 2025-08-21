# config.py
import os


class Config:
    BANGKOK_LAT = 13.7563
    BANGKOK_LON = 100.5018
    FETCH_INTERVAL_SECONDS = int(os.getenv("FETCH_INTERVAL_SECONDS", 5))
    LAST_EVENT_FILE = os.getenv("LAST_EVENT_FILE", "last_event.txt")
    CHAT_ID_FILE = os.getenv("CHAT_ID_FILE", "chat_id.txt")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Bangkok")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # optional fallback
