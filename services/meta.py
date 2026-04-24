import requests
from config import PAGE_ACCESS_TOKEN

def enviar_mensaje(user_id, texto):
    url = "https://graph.facebook.com/v19.0/me/messages"

    response = requests.post(
        url,
        params={"access_token": PAGE_ACCESS_TOKEN},
        json={
            "recipient": {"id": user_id},
            "message": {"text": texto}
        }
    )

    return response.json()