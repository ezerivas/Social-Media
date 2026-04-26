from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse

from config import VERIFY_TOKEN
from database import engine, Base, SessionLocal
from crud import save_message
from database import SessionLocal
from models import Conversation

import json

app = FastAPI()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


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

                db = SessionLocal()
                try:
                    save_message(db, sender_id, text)
                finally:
                    db.close()

    return {"status": "ok"}


@app.get("/conversations")
def get_conversations():
    db = SessionLocal()

    try:
        conversations = db.query(Conversation).all()

        result = []
        for c in conversations:
            result.append({
                "id": c.id,
                "user_id": c.user_id,
                "canal": c.canal,
                "estado": c.estado,
                "last_message_at": c.last_message_at
            })

        return result

    finally:
        db.close()


@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    db = SessionLocal()

    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).all()

        result = []
        for m in messages:
            result.append({
                "id": m.id,
                "sender": m.sender,
                "text": m.text,
                "timestamp": m.timestamp
            })

        return result

    finally:
        db.close()