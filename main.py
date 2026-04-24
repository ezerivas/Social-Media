from fastapi import FastAPI, Request
from config import VERIFY_TOKEN
import json

app = FastAPI()

# ---------------------------
# Ruta base (para testear)
# ---------------------------
@app.get("/")
def home():
    return {"status": "ok"}


# ---------------------------
# Verificación del webhook (GET)
# ---------------------------
@app.get("/webhook")
def verify(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)

    return {"error": "verification failed"}


# ---------------------------
# Recepción de mensajes (POST)
# ---------------------------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("EVENT:")
    print(json.dumps(data, indent=2))

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):

            sender_id = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text")

                print(f"Usuario {sender_id}: {text}")

                # 👉 acá después vas a:
                # guardar en base de datos
                # generar respuesta con IA
                # enviar respuesta

    return {"status": "ok"}