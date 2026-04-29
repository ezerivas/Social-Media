import httpx
from typing import Dict, Any
from app.channels.base import BaseChannel

class FacebookChannel(BaseChannel):
    """Lógica para interactuar con la Graph API de Facebook"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Se inicializa con el diccionario 'config' que viene de la tabla 'channels'.
        Estructura esperada en DB: {"access_token": "...", "page_id": "..."}
        """
        self.access_token = config.get("access_token")
        self.page_id = config.get("page_id")
        self.api_url = f"https://graph.facebook.com/v19.0/{self.page_id}/messages"

    async def send_text(self, recipient_id: str, text: str):
        """Envía un mensaje de texto plano a un usuario"""
        if not self.access_token or not self.page_id:
            raise ValueError("Configuración de Facebook incompleta (faltan tokens)")

        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "RESPONSE"  # Cambiado a RESPONSE para respuestas estándar
        }
        
        # Nota: Meta requiere tags solo si el mensaje es fuera de la ventana de 24h.
        # Para pruebas iniciales, 'RESPONSE' es lo más seguro.

        params = {"access_token": self.access_token}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Loggear el error detallado de Facebook ayuda mucho en el debug
                print(f"❌ Error de Facebook API: {e.response.text}")
                raise e

    async def send_image(self, recipient_id: str, image_url: str):
        """Opcional: Envío de imágenes si lo necesitas después"""
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {"url": image_url, "is_reusable": True}
                }
            }
        }
        params = {"access_token": self.access_token}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, params=params)
            return response.json()