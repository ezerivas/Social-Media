from fastapi import APIRouter, Request
from core.tenant_resolver import resolve_tenant
from services.messaging import handle_incoming_message

router = APIRouter()

@router.get("/webhook/facebook")
async def verify(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    print("VERIFY HIT", params)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return {"error": "verification failed"}

@router.post("/webhook/facebook")
async def webhook(request: Request):
    data = await request.json()
    tenant_id = resolve_tenant(request)

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):

            sender = messaging["sender"]["id"]

            if "message" in messaging:
                text = messaging["message"].get("text")

                await handle_incoming_message(
                    tenant_id,
                    "facebook",
                    sender,
                    text
                )

    return {"status": "ok"}