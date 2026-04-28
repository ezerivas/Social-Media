from fastapi import FastAPI, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, FileResponse
import requests
import asyncio

from config import VERIFY_TOKEN, PAGE_ACCESS_TOKEN
from services.messaging import handle_incoming_message
from repositories.conversations import get_all_conversations, update_last_message
from repositories.messages import get_messages_by_conversation, create_message
from ws_manager import connect, disconnect, send_to_room

app = FastAPI()


# ---------- FRONT ----------
@app.get("/")
def home():
    return FileResponse("index.html")


# ---------- WEBSOCKET POR CONVERSACIÓN ----------
@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(ws: WebSocket, conversation_id: int):
    await connect(ws, conversation_id)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        disconnect(ws, conversation_id)


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

                conversation = handle_incoming_message(sender_id, text)
                conversation_id = conversation[0]

                asyncio.create_task(send_to_room(conversation_id, {
                    "type": "new_message",
                    "conversation_id": conversation_id
                }))

    return {"status": "ok"}


# ---------- ENVIAR MENSAJE ----------
@app.post("/send")
async def send(data: dict):
    recipient_id = data.get("recipient_id")
    text = data.get("text")
    conversation_id = data.get("conversation_id")

    if not recipient_id or not text or not conversation_id:
        return {"error": "missing data"}

    # guardar en DB
    create_message(conversation_id, "assistant", text)
    update_last_message(conversation_id)

    # enviar a Facebook (opcional)
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    try:
        requests.post(url, params=params, json=payload)
    except:
        pass

    # realtime
    asyncio.create_task(send_to_room(conversation_id, {
        "type": "new_message",
        "conversation_id": conversation_id
    }))

    return {"status": "sent"}


# ---------- API ----------
@app.get("/conversations")
def conversations():
    return get_all_conversations()


@app.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int):
    return get_messages_by_conversation(conversation_id)