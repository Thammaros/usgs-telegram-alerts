import requests
from logger import logger
from storage import read_cached_chat_id, save_cached_chat_id


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.chat_id = None  # Will be auto-filled after fetching updates

    def send_photo(self, image_path: str, caption: str = None) -> None:
        if not self.chat_id:
            logger.warning("⚠️ Chat ID not set.")
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
                logger.info("✅ Image sent to Telegram.")
        except Exception as e:
            logger.error(f"❌ Failed to send image: {e}")

    def send_message(self, message: str) -> None:
        if not self.chat_id:
            logger.warning(
                "⚠️ Chat ID not set. Call 'load_or_fetch_chat_id()' first or set it manually."
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
            logger.info("✅ Telegram message sent successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")

    def get_updates(self, limit: int = 5) -> dict:
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url, params={"limit": limit})
            response.raise_for_status()
            updates = response.json()
            logger.info(f"📥 Retrieved {len(updates.get('result', []))} update(s).")
            return updates
        except Exception as e:
            logger.error(f"❌ Failed to fetch updates: {e}")
            return {}

    def extract_chat_id(self) -> int | None:
        updates = self.get_updates(limit=1)
        results = updates.get("result", [])

        if not results:
            logger.warning("⚠️ No messages found. Send a message to the bot first.")
            return None

        try:
            message = results[0]["message"]
            chat_id = message["chat"]["id"]
            chat_title = message["chat"].get("title") or message["chat"].get(
                "username", "Unknown"
            )
            self.chat_id = chat_id
            logger.info(f"✅ Extracted chat ID: {chat_id} ({chat_title})")
            return chat_id
        except KeyError as e:
            logger.error(f"❌ Unexpected structure in update: {e}")
            return None

    def load_or_fetch_chat_id(self) -> int | None:
        cached_chat_id = read_cached_chat_id()
        if cached_chat_id:
            logger.info(f"✅ Loaded cached chat ID: {cached_chat_id}")
            self.chat_id = cached_chat_id
            return cached_chat_id

        chat_id = self.extract_chat_id()
        if chat_id:
            save_cached_chat_id(chat_id)
            logger.info(f"✅ Fetched and cached chat ID: {chat_id}")
            return chat_id

        logger.error("❌ Failed to obtain chat ID. Please message your bot first.")
        return None
