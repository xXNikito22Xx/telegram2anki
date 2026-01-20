"""
Telegram client for fetching and managing messages from the bot.
"""
import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class TelegramClient:
    """Client to interact with Telegram Bot API."""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def get_messages(self, since_days: int = 7) -> List[Dict]:
        """
        Fetch messages from the bot's chat history.
        
        Note: Telegram Bot API doesn't provide direct message history access.
        We use getUpdates which stores messages for 24 hours.
        For longer storage, we'll use a simple file-based approach.
        """
        messages = []
        
        # Try to get updates (works for recent messages)
        response = requests.get(
            f"{self.base_url}/getUpdates",
            params={"offset": -100, "limit": 100}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                for update in data.get("result", []):
                    message = update.get("message", {})
                    if message.get("chat", {}).get("id") == int(self.chat_id):
                        text = message.get("text", "")
                        if text and not text.startswith("/"):
                            messages.append({
                                "id": message.get("message_id"),
                                "text": text,
                                "date": datetime.fromtimestamp(message.get("date", 0))
                            })
        
        return messages
    
    def send_message(self, text: str) -> bool:
        """Send a message to the chat."""
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
        )
        return response.status_code == 200
    
    def delete_message(self, message_id: int) -> bool:
        """Delete a message from the chat."""
        response = requests.post(
            f"{self.base_url}/deleteMessage",
            json={
                "chat_id": self.chat_id,
                "message_id": message_id
            }
        )
        return response.status_code == 200


def get_pending_messages_from_file(filepath: str) -> List[Dict]:
    """
    Read pending messages from a local file.
    This is used as a workaround for Telegram's 24-hour update limit.
    """
    messages = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append({"text": line, "id": None})
    return messages


def clear_pending_messages_file(filepath: str):
    """Clear the pending messages file after processing."""
    if os.path.exists(filepath):
        os.remove(filepath)
