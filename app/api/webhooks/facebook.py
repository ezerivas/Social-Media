from fastapi import APIRouter, Query, Request, Response

from app.core.config import settings
from app.services.messaging import MessagingService
from app.ws.manager import manager

router = APIRouter()


@router.get("/facebook")
async def verify_facebook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.FACEBOOK_VERIFY_TOKEN:
        return Response(content=str(hub_challenge), media_type="text/plain")

    return Response(content="Error de validación", status_code=403)


@router.post("/facebook")
async def handle_facebook_events(request: Request):
    payload = await request.json()
    service = MessagingService(request.app.state.db_pool, ws_manager=manager)

    # TODO: resolver tenant dinámicamente con el page_id/token.
    tenant_id = 1

    try:
        await service.handle_inbound_message(
            channel_name="facebook",
            payload=payload,
            tenant_id=tenant_id,
        )
        return {"status": "success"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
