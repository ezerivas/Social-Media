from fastapi import FastAPI, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, FileResponse
import requests
import json

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

                # guarda en DB
                conversation_id = handle_incoming_message(sender_id, text)

                # enviar en vivo por WS
                await send_to_room(conversation_id, {
                    "role": "user",
                    "content": text
                })

    return {"status": "ok"}


# ---------- WEBSOCKET ----------
@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(ws: WebSocket, conversation_id: int):
    await connect(ws, conversation_id)

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "message":
                text = msg.get("text")

                # guardar en DB
                message = create_message(conversation_id, "assistant", text)

                # actualizar conversación
                update_last_message(conversation_id)

                # enviar a todos los clientes
                await send_to_room(conversation_id, {
                    "id": message[0],
                    "role": message[2],
                    "content": message[3],
                    "created_at": str(message[4])
                })

    except WebSocketDisconnect:
        disconnect(ws, conversation_id)


# ---------- API DASHBOARD ----------
@app.get("/conversations")
def conversations():
    return get_all_conversations()


@app.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int):
    return get_messages_by_conversation(conversation_id)