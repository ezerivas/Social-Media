import requests
from config import PAGE_ACCESS_TOKEN

# obtener nombre del usuario desde Facebook
def get_user_name(psid: str):
    url = f"https://graph.facebook.com/{psid}"

    params = {
        "fields": "name",
        "access_token": PAGE_ACCESS_TOKEN
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        return data.get("name", "Usuario")
    except Exception as e:
        print("ERROR META:", e)
        return "Usuario"