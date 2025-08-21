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
        self.session = httpx.Client(timeout=10)
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.chat_id = int(Config.TELEGRAM_CHAT_ID)

    def send_photo(self, image_path: str, caption: str = None) -> None:

        try:
            url = f"{self.base_url}/sendPhoto"
            with open(image_path, "rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": self.chat_id}
                if caption:
                    data["caption"] = caption
                response = self.session.post(url, files=files, data=data)
                response.raise_for_status()
                logger.info("Image sent successfully via Telegram.")
        except Exception as e:
            logger.error(f"Failed to send image via Telegram: {e}")

    def send_message(self, message: str) -> None:
        if not self.chat_id:
            logger.warning(
                "Chat ID is not set. Ensure 'load_or_fetch_chat_id()' has been called."
            )
            return

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            logger.info("Text message sent successfully via Telegram.")
        except Exception as e:
            logger.error(f"Failed to send text message via Telegram: {e}")

    def close(self) -> None:
        try:
            self.session.close()
        except Exception:
            pass
