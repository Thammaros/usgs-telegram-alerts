import requests
from logger import logger
from storage import read_cached_chat_id, save_cached_chat_id


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.chat_id = None  # Automatically retrieved or loaded

    def send_photo(self, image_path: str, caption: str = None) -> None:
        if not self.chat_id:
            logger.warning("Chat ID is not set. Photo message was not sent.")
            return

        try:
            url = f"{self.base_url}/sendPhoto"
            with open(image_path, "rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": self.chat_id}
                if caption:
                    data["caption"] = caption
                response = requests.post(url, files=files, data=data)
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
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info("Text message sent successfully via Telegram.")
        except Exception as e:
            logger.error(f"Failed to send text message via Telegram: {e}")

    def get_updates(self, limit: int = 5) -> dict:
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url, params={"limit": limit})
            response.raise_for_status()
            updates = response.json()
            logger.info(
                f"Received {len(updates.get('result', []))} Telegram update(s)."
            )
            return updates
        except Exception as e:
            logger.error(f"Failed to fetch Telegram updates: {e}")
            return {}

    def extract_chat_id(self) -> int | None:
        updates = self.get_updates(limit=1)
        results = updates.get("result", [])

        if not results:
            logger.warning(
                "No Telegram messages received. Please send a message to the bot."
            )
            return None

        try:
            message = results[0]["message"]
            chat_id = message["chat"]["id"]
            chat_title = message["chat"].get("title") or message["chat"].get(
                "username", "Unknown"
            )
            self.chat_id = chat_id
            logger.info(f"Extracted chat ID: {chat_id} ({chat_title})")
            return chat_id
        except KeyError as e:
            logger.error(f"Unexpected response structure while extracting chat ID: {e}")
            return None

    def load_or_fetch_chat_id(self) -> int | None:
        cached_chat_id = read_cached_chat_id()
        if cached_chat_id:
            logger.info(f"Using cached chat ID: {cached_chat_id}")
            self.chat_id = cached_chat_id
            return cached_chat_id

        chat_id = self.extract_chat_id()
        if chat_id:
            save_cached_chat_id(chat_id)
            logger.info(f"Fetched and cached new chat ID: {chat_id}")
            return chat_id

        logger.error(
            "Unable to obtain chat ID. Ensure the bot has received at least one message."
        )
        return None
