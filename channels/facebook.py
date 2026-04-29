import httpx
from .base import IBaseChannel

class FacebookChannel(IBaseChannel):
    async def send_text(self, to_external_id: str, message_text: str, config: dict) -> str:
        # Usa el token guardado dinámicamente para este tenant/canal
        url = f"https://graph.facebook.com/v19.0/{config['page_id']}/messages"
        payload = {
            "recipient": {"id": to_external_id},
            "message": {"text": message_text},
            "access_token": config['access_token']
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json().get("message_id")