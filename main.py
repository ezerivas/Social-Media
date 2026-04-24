from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from config import VERIFY_TOKEN
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
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error")


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("EVENT:")
    print(json.dumps(data, indent=2))

    return {"status": "ok"}