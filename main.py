from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse

from config import VERIFY_TOKEN
from database import engine, Base, SessionLocal
from crud import save_message

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