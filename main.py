from fastapi import FastAPI, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, FileResponse

from config import VERIFY_TOKEN, PAGE_ACCESS_TOKEN
from services.messaging import handle_incoming_message
from repositories.conversations import get_all_conversations
from repositories.messages import get_messages
from ws_manager import connect, disconnect, send_to_room

import requests

app = FastAPI()


def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v18.0/me/messages"

    params = {"access_token": PAGE_ACCESS_TOKEN}

    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    requests.post(url, params=params, json=data)


@app.get("/")
def home():
    return FileResponse("index.html")


@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int):
    await connect(websocket, conversation_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        disconnect(websocket, conversation_id)


@app.post("/send")
async def send(data: dict):
    recipient_id = data.get("recipient_id")
    text = data.get("text")

    send_message(recipient_id, text)

    conv_id = handle_incoming_message(recipient_id, text, sender="agent")

    await send_to_room(conv_id, {"type": "new_message"})

    return {"status": "sent"}


@app.get("/webhook")
def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error")


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text")

                conv_id = handle_incoming_message(sender_id, text, "user")

                await send_to_room(conv_id, {"type": "new_message"})

    return {"status": "ok"}


@app.get("/conversations")
def conversations():
    return get_all_conversations()


@app.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int):
    return get_messages(conversation_id)