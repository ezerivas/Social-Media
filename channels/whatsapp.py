import requests
from channels.base import BaseChannel


class WhatsAppChannel(BaseChannel):

    def send(self, config, recipient_id, text):
        url = "https://graph.facebook.com/v18.0/messages"

        headers = {
            "Authorization": f"Bearer {config['token']}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {"body": text}
        }

        requests.post(url, headers=headers, json=payload)