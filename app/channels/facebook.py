from typing import Any, Dict, Optional

import httpx

from app.channels.base import BaseChannel


class FacebookChannel(BaseChannel):
    GRAPH_API_BASE_URL = "https://graph.facebook.com/v19.0"

    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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

    async def send_text(self, recipient_id: str, message_text: str, config: Dict[str, Any]) -> bool:
        access_token = config.get("access_token")
        page_id = config.get("page_id")
        if not access_token or not page_id:
            raise ValueError("Configuración de Facebook incompleta")

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
        return True
