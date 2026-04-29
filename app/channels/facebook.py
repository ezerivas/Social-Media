import httpx
from app.channels.base import BaseChannel

class FacebookChannel(BaseChannel):
    """Lógica para interactuar con la Graph API de Facebook"""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.api_url = f"https://graph.facebook.com/v19.0/{page_id}/messages"

    async def send_text(self, recipient_id: str, text: str):
        """Envía un mensaje de texto plano a un usuario"""
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "MESSAGE_TAG",
            "tag": "ACCOUNT_UPDATE" # O el tag correspondiente según política de Meta
        }
        params = {"access_token": self.access_token}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, params=params)
            response.raise_for_status()
            return response.json()