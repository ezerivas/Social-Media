import requests
from channels.base import BaseChannel


class InstagramChannel(BaseChannel):

    def send(self, config, recipient_id, text):
        url = "https://graph.facebook.com/v18.0/me/messages"

        params = {"access_token": config["token"]}

        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }

        requests.post(url, params=params, json=payload)