# telegram.py
import httpx
from logger import logger
from config import Config


class TelegramBot:
    def __init__(self, token: str = None):
        self.token = token or Config.TELEGRAM_BOT_TOKEN
        if not self.token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN must be set in environment or passed in."
            )
        if not Config.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID must be set in environment.")
        self.session = httpx.AsyncClient(timeout=10)
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.chat_id = int(Config.TELEGRAM_CHAT_ID)

    async def send_photo(self, image_path: str, caption: str | None = None) -> None:
        url = f"{self.base_url}/sendPhoto"
        try:
            # Opening a small local file is fast; a normal context manager is fine.
            with open(image_path, "rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": self.chat_id}
                if caption:
                    data["caption"] = caption
                resp = await self.session.post(url, files=files, data=data)
                resp.raise_for_status()
                logger.info("Image sent successfully via Telegram.")
        except Exception as e:
            logger.error(f"Failed to send image via Telegram: {e}")

    async def send_message(self, message: str) -> None:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        try:
            resp = await self.session.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Text message sent successfully via Telegram.")
        except Exception as e:
            logger.error(f"Failed to send text message via Telegram: {e}")

    async def aclose(self) -> None:
        try:
            await self.session.aclose()
        except Exception:
            pass
