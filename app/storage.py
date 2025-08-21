# storage.py
import os
from config import Config
from typing import Set


def read_last_event_id() -> Set[str]:
    if not os.path.exists(Config.LAST_EVENT_FILE):
        return set()
    with open(Config.LAST_EVENT_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_last_event_id(event_id: str) -> None:
    with open(Config.LAST_EVENT_FILE, "a") as file:
        file.write(f"{event_id}\n")
