from fastapi import FastAPI, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, FileResponse
import json

from core.config import VERIFY_TOKEN

from services.messaging import (
    handle_incoming_message,
    handle_outgoing_message
)

from repositories.conversations import get_all_conversations
from repositories.messages import get_messages_by_conversation

from ws.manager import connect, disconnect

app = FastAPI()


# =========================================================
# 🌐 FRONT
# =========================================================
@app.get("/")
def home():
    return FileResponse("index.html")


# =========================================================
# 🔐 VERIFY (Facebook / IG usan esto)
# =========================================================
@app.get("/webhook/facebook")
def verify_facebook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error")


@app.get("/webhook/instagram")
def verify_instagram(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error")


# =========================================================
# 📥 WEBHOOK FACEBOOK
# =========================================================
@app.post("/webhook/facebook")
async def webhook_facebook(request: Request):
    data = await request.json()

    tenant_id = 1  # ⚠️ luego dinámico

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):

            sender_id = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text")

                await handle_incoming_message(
                    tenant_id=tenant_id,
                    channel="facebook",
                    external_user_id=sender_id,
                    text=text
                )

    return {"status": "ok"}


# =========================================================
# 📥 WEBHOOK INSTAGRAM
# =========================================================
@app.post("/webhook/instagram")
async def webhook_instagram(request: Request):
    data = await request.json()

    tenant_id = 1  # ⚠️ luego dinámico

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):

            sender_id = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text")

                await handle_incoming_message(
                    tenant_id=tenant_id,
                    channel="instagram",
                    external_user_id=sender_id,
                    text=text
                )

    return {"status": "ok"}


# =========================================================
# 📥 WEBHOOK WHATSAPP (META CLOUD API)
# =========================================================
@app.post("/webhook/whatsapp")
async def webhook_whatsapp(request: Request):
    data = await request.json()

    tenant_id = 1  # ⚠️ luego dinámico

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            msg = value["messages"][0]

            sender_id = msg["from"]
            text = msg["text"]["body"]

            await handle_incoming_message(
                tenant_id=tenant_id,
                channel="whatsapp",
                external_user_id=sender_id,
                text=text
            )

    except Exception as e:
        print("WhatsApp webhook error:", e)

    return {"status": "ok"}


# =========================================================
# 🔌 WEBSOCKET (REALTIME)
# =========================================================
@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(ws: WebSocket, conversation_id: int):
    await connect(ws, conversation_id)

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "message":
                text = msg.get("text")
                tenant_id = 1  # ⚠️ luego dinámico

                await handle_outgoing_message(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    text=text
                )

    except WebSocketDisconnect:
        disconnect(ws, conversation_id)


# =========================================================
# 📊 API DASHBOARD
# =========================================================
@app.get("/conversations")
def conversations():
    return get_all_conversations()


@app.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int):
    return get_messages_by_conversation(conversation_id)