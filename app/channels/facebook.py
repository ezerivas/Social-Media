"""
Facebook Messenger channel implementation.
"""
import logging
from typing import Any, Dict, Optional

import httpx

from app.channels.base import BaseChannel

logger = logging.getLogger(__name__)


class FacebookChannel(BaseChannel):
    """Facebook Messenger channel adapter."""

    GRAPH_API_BASE_URL = "https://graph.facebook.com/v19.0"

    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Facebook Messenger webhook payload.

        Expected format:
        {
            "entry": [{
                "messaging": [{
                    "sender": {"id": "..."},
                    "message": {"text": "..."}
                }]
            }]
        }
        """
        entries = payload.get("entry", [])
        for entry in entries:
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                message_text = messaging_event.get("message", {}).get("text")
                if sender_id and message_text:
                    return {
                        "sender_id": sender_id,
                        "text": message_text,
                    }
        return None

    async def send_text(
        self,
        recipient_id: str,
        message_text: str,
        config: Dict[str, Any],
    ) -> bool:
        """
        Send a text message via Facebook Graph API.

        Args:
            recipient_id: Facebook user ID
            message_text: Message content
            config: Channel config with access_token and page_id

        Returns:
            True if sent successfully
        """
        access_token = config.get("access_token")
        page_id = config.get("page_id")

        if not access_token or not page_id:
            logger.error("Facebook configuration incomplete")
            raise ValueError("Facebook configuration incomplete")

        api_url = f"{self.GRAPH_API_BASE_URL}/{page_id}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "messaging_type": "RESPONSE",
        }
        params = {"access_token": access_token}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(api_url, json=payload, params=params)
            response.raise_for_status()

        logger.info("Message sent to Facebook user: %s", recipient_id)
        return True
