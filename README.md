# USGS Telegram Earthquake Alert

A lightweight, Dockerized Python service that monitors earthquake activity via the [USGS Earthquake API](https://earthquake.usgs.gov/) and sends real-time alerts (including maps) to Telegram when events occur within 2,500 km of Bangkok, Thailand and have a magnitude greater than 5.0.

---

## Project Structure

```
.
├── docker-compose.yaml     # Docker orchestration
├── deploy.sh               # Optional script for deployment
└── app/
    ├── main.py             # Main monitoring loop
    ├── config.py           # Configuration (API keys, constants)
    ├── mapgen.py           # Cartopy-based map generator
    ├── storage.py          # Read/write cache for event/chat ID
    ├── telegram.py         # Telegram bot interface
    ├── usgs_api.py         # USGS API integration
    ├── logger.py           # Logging setup
    ├── requirements.txt    # Python dependencies
    └── Dockerfile          # Alpine-based build config
```

---

## Features

- Periodically queries the USGS API every 15 seconds
- Calculates geodesic distance from Bangkok to epicenter
- Sends alerts via Telegram (only for quakes within 2,500 km and magnitude > 5.0)
- Renders and sends annotated map images using Cartopy
- Stores previously notified earthquake IDs to prevent duplicates
- Containerized using a lightweight Alpine-based Python image

---

## Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/Thammaros/usgs-telegram-alerts.git
cd usgs-telegram-alerts
```

### 2. Configure Telegram Bot

Edit `app/config.py` and set your bot token:

```python
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
```

> Note: You must message your bot once via Telegram to allow it to read your chat ID automatically.

### 3. Run via Docker Compose

```bash
docker compose up -d --build
```

This command will:

- Build the container image
- Mount a volume for persistent storage of `last_event.txt` and `chat_id.txt`
- Start a long-running background service

---

## Runtime Behavior

- Earthquakes are checked every 15 seconds (configurable)
- Telegram alerts are sent only if:
  - Magnitude > 5.0
  - Within 2,500 km of Bangkok
  - Not previously notified (based on event ID)
- Map images are generated and sent alongside detailed info (in Thai)

---

## Example Output

![Example Output](https://github.com/user-attachments/assets/cf795063-3da7-4cb0-989b-1917f3815c12)

> Sample includes annotated epicenter, Bangkok marker, and distance label

---

## Python Dependencies

- [`cartopy`](https://scitools.org.uk/cartopy/)
- `matplotlib`
- `geopy`
- `requests`
- `python-telegram-bot`

> System dependencies (GEOS, PROJ, etc.) handled in the Alpine-based Dockerfile.

---

## Clean Up

To stop and remove the container and volume:

```bash
docker compose down -v
```

---

## License

This project is licensed under the MIT License. See [`LICENSE`](./LICENSE) for details.

---

## Acknowledgements

- USGS Earthquake API
- Telegram Bot API
- Cartopy (Geospatial Visualization)

---

## Author

Maintained by [Thammaros](https://github.com/Thammaros)

