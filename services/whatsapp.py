import requests


def send(config: dict, recipient_id: str, text: str):
    token = config.get("access_token")
    phone_number_id = config.get("phone_number_id")

    if not token or not phone_number_id:
        raise ValueError("Missing WhatsApp config (token or phone_number_id)")

    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": text
        }
    }

    try:
        res = requests.post(url, headers=headers, json=payload)

        if res.status_code not in (200, 201):
            raise Exception(f"WhatsApp API error: {res.text}")

        return res.json()

    except Exception as e:
        print("WhatsApp send error:", e)
        return None