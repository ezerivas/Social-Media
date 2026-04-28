from fastapi import APIRouter, Request
from core.tenant_resolver import resolve_tenant
from services.messaging import handle_incoming_message

router = APIRouter()


@router.post("/webhook/whatsapp")
async def webhook(request: Request):
    data = await request.json()
    tenant_id = resolve_tenant(request)

    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = msg["from"]
        text = msg["text"]["body"]

        await handle_incoming_message(
            tenant_id,
            "whatsapp",
            sender,
            text
        )

    except:
        pass

    return {"status": "ok"}