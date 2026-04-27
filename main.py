from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse, FileResponse

from config import VERIFY_TOKEN
from database import engine, Base, SessionLocal
from crud import save_message
from models import Conversation, Message, User

import requests
import os

app = FastAPI()

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")


# 🔹 enviar mensaje a Facebook
def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v18.0/me/messages"

    params = {"access_token": PAGE_ACCESS_TOKEN}

    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    response = requests.post(url, params=params, json=data)
    print("SEND RESPONSE:", response.text)


# 🔹 endpoint enviar mensaje
@app.post("/send")
async def send(data: dict):
    recipient_id = data.get("recipient_id")
    text = data.get("text")

    if not recipient_id or not text:
        return {"error": "faltan datos"}

    # enviar a Facebook
    send_message(recipient_id, text)

    # guardar en DB como agente
    db = SessionLocal()
    try:
        save_message(db, recipient_id, text, sender="agent")
    finally:
        db.close()

    return {"status": "sent"}


# 🔹 servir frontend
@app.get("/")
def home():
    return FileResponse("index.html")


# 🔹 crear tablas
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# 🔹 verificación webhook
@app.get("/webhook")
def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error")


# 🔹 recibir mensajes
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):

            sender_id = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text")

                db = SessionLocal()
                try:
                    save_message(db, sender_id, text, sender="user")
                finally:
                    db.close()

    return {"status": "ok"}


# 🔹 listar conversaciones
@app.get("/conversations")
def get_conversations():
    db = SessionLocal()

    try:
        conversations = db.query(Conversation)\
            .order_by(Conversation.last_message_at.desc())\
            .all()

        result = []

        for c in conversations:
            user = db.query(User).filter(User.id == c.user_id).first()

            last_message = db.query(Message)\
                .filter(Message.conversation_id == c.id)\
                .order_by(Message.timestamp.desc())\
                .first()

            result.append({
                "id": c.id,
                "user_id": c.user_id,
                "external_id": user.external_id if user else None,
                "canal": c.canal,
                "estado": c.estado,
                "last_message_at": c.last_message_at,
                "last_message": last_message.text if last_message else None
            })

        return result

    finally:
        db.close()


# 🔹 mensajes de una conversación
@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    db = SessionLocal()

    try:
        messages = db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(Message.timestamp.asc())\
            .all()

        result = []

        for m in messages:
            result.append({
                "id": m.id,
                "sender": m.sender,
                "text": m.text,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None
            })

        return result

    finally:
        db.close()