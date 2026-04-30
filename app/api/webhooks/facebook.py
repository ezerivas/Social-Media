from fastapi import APIRouter, Request, Depends, Query, Response
from app.repositories.messages import MessageRepository
from app.core.config import settings
from app.ws.manager import manager

router = APIRouter()

async def get_repo(request: Request):
    return MessageRepository(request.app.state.db_pool)

# ✅ Verificación webhook
@router.get("/facebook")
async def verify_facebook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.FACEBOOK_VERIFY_TOKEN:
        return Response(content=str(hub_challenge), media_type="text/plain")

    return Response(content="Error de validación", status_code=403)


# ✅ Webhook + realtime
@router.post("/facebook")
async def handle_facebook_events(
    request: Request,
    repo: MessageRepository = Depends(get_repo)
):
    payload = await request.json()

    try:
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):

                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event.get("message", {}).get("text")

                if not message_text:
                    continue

                message = await repo.save_message(
                    tenant_id=1,
                    user_external_id=sender_id,
                    channel="facebook",
                    content=message_text,
                    role="user"
                )

                print(f"✅ Guardado: {message_text}")

                # 🔥 DEBUG IMPORTANTE
                print("📡 Enviando por WS...")

                await manager.broadcast_to_tenant(
                    1,
                    {
                        "event": "new_message",
                        "data": {
                            "text": message_text,
                            "sender": sender_id
                        }
                    }
                )

        return {"status": "success"}

    except Exception as e:
        print("❌ Webhook error:", e)
        return {"status": "error", "message": str(e)}