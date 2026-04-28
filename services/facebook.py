import requests


GRAPH_API_URL = "https://graph.facebook.com/v18.0/me/messages"


def send(config: dict, recipient_id: str, text: str):
    access_token = config.get("access_token")

    if not access_token:
        raise ValueError("Missing access_token in Facebook config")

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    params = {
        "access_token": access_token
    }

    try:
        res = requests.post(GRAPH_API_URL, params=params, json=payload)

        if res.status_code != 200:
            raise Exception(f"Facebook API error: {res.text}")

        return res.json()

    except Exception as e:
        print("Facebook send error:", e)
        return None