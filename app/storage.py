import os
from config import Config


def read_last_event_id() -> str:
    if not os.path.exists(Config.LAST_EVENT_FILE):
        return set()
    with open(Config.LAST_EVENT_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_last_event_id(event_id: str) -> None:
    with open(Config.LAST_EVENT_FILE, "a") as file:
        file.write(f"{event_id}\n")


def read_cached_chat_id() -> int | None:
    if os.path.exists(Config.CHAT_ID_FILE):
        with open(Config.CHAT_ID_FILE, "r") as file:
            try:
                return int(file.read().strip())
            except ValueError:
                return None
    return None


def save_cached_chat_id(chat_id: int) -> None:
    with open(Config.CHAT_ID_FILE, "w") as file:
        file.write(str(chat_id))
