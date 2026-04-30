"""
Facebook webhook handler.
"""
import logging

from fastapi import APIRouter, Query, Request, Response
from pydantic import BaseModel

from app.core.config import settings
from app.services.messaging import MessagingService
from app.ws.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


class WebhookResponse(BaseModel):
    """Response model for webhook operations."""
    status: str
    message: str = ""


@router.get("/facebook")
async def verify_facebook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
) -> Response:
    """
    Verify webhook for Facebook Messenger platform.
    """
    logger.debug("Facebook webhook verification: mode=%s", hub_mode)

    if hub_mode == "subscribe" and hub_verify_token == settings.FACEBOOK_VERIFY_TOKEN:
        logger.info("Facebook webhook verified successfully")
        return Response(content=str(hub_challenge), media_type="text/plain")

    logger.warning("Facebook webhook verification failed")
    return Response(content="Verification failed", status_code=403)


@router.post("/facebook", response_model=WebhookResponse)
async def handle_facebook_events(request: Request) -> WebhookResponse:
    """
    Handle incoming Facebook Messenger events.
    """
    payload = await request.json()
    logger.debug("Received Facebook event: %s", payload)

    service = MessagingService(request.app.state.db_pool, ws_manager=manager)

    # TODO: Resolve tenant dynamically using page_id/token
    tenant_id = 1

    try:
        await service.handle_inbound_message(
            channel_name="facebook",
            payload=payload,
            tenant_id=tenant_id,
        )
        logger.info("Facebook event processed successfully")
        return WebhookResponse(status="success")
    except Exception as exc:
        logger.error("Error processing Facebook event: %s", exc)
        return WebhookResponse(status="error", message=str(exc))
