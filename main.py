from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse, FileResponse
import requests

from config import VERIFY_TOKEN, PAGE_ACCESS_TOKEN
from services.messaging import handle_incoming_message
from repositories.conversations import get_all_conversations
from repositories.messages import get_messages_by_conversation

app = FastAPI()


# ---------- FRONT ----------
@app.get("/")
def home():
    return FileResponse("index.html")


# ---------- WEBHOOK VERIFY ----------
@app.get("/webhook")
def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error")


# ---------- WEBHOOK RECEIVE ----------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text")
                handle_incoming_message(sender_id, text)

    return {"status": "ok"}


# ---------- ENVIAR MENSAJE ----------
@app.post("/send")
async def send(data: dict):
    recipient_id = data.get("recipient_id")
    text = data.get("text")

    if not recipient_id or not text:
        return {"error": "missing data"}

    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    requests.post(url, params=params, json=payload)

    return {"status": "sent"}


# ---------- API DASHBOARD ----------
@app.get("/conversations")
def conversations():
    return get_all_conversations()


@app.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int):
    return get_messages_by_conversation(conversation_id)