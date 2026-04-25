from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from config import VERIFY_TOKEN
from sheets import guardar_mensaje
import json

app = FastAPI()


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/webhook")
def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(str(hub_challenge))

    return PlainTextResponse("error", status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("EVENT:")
    print(json.dumps(data, indent=2))

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):

            sender_id = messaging.get("sender", {}).get("id")

            message = messaging.get("message", {})
            text = message.get("text")

            if sender_id and text:
                print(f"Usuario {sender_id}: {text}")

                try:
                    guardar_mensaje(sender_id, text)
                except Exception as e:
                    print("ERROR Sheets:", e)

    return {"status": "ok"}