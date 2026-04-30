"""
Message API routes.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from pydantic import BaseModel, Field

from app.repositories.messages import MessageRepository
from app.services.messaging import MessagingService
from app.ws.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────


class MessageRequest(BaseModel):
    """Request model for sending a message."""
    conversation_id: int = Field(..., description="Conversation ID")
    content: str = Field(..., min_length=1, description="Message content")


class ChannelResponse(BaseModel):
    """Response model for a channel."""
    id: str
    name: str
    enabled: bool


class ConversationListResponse(BaseModel):
    """Response model for conversation list."""
    data: list


class MessageListResponse(BaseModel):
    """Response model for message list."""
    data: list


class SendMessageResponse(BaseModel):
    """Response model for sending a message."""
    status: str
    message: str
    data: Optional[dict] = None


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────


def resolve_tenant_id(request: Request) -> int:
    """Extract tenant ID from request state or use default."""
    return getattr(request.state, "tenant_id", 1)


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────


@router.get("/channels", response_model=list[ChannelResponse])
async def list_channels():
    """
    List available messaging channels.
    """
    logger.debug("Listing available channels")
    return [
        {"id": "facebook", "name": "Facebook", "enabled": True},
        {"id": "instagram", "name": "Instagram", "enabled": False},
        {"id": "whatsapp", "name": "WhatsApp", "enabled": False},
    ]


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    request: Request,
    channel: str = Query(..., description="Channel identifier"),
):
    """
    List conversations for a specific channel.
    """
    tenant_id = resolve_tenant_id(request)
    logger.info(f"Listing conversations: tenant_id=%s, channel=%s", tenant_id, channel)

    repo = MessageRepository(request.app.state.db_pool)
    conversations = await repo.list_conversations(tenant_id=tenant_id, channel=channel)

    return {"data": conversations}


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def list_conversation_messages(
    request: Request,
    conversation_id: int = Path(..., description="Conversation ID"),
):
    """
    List messages for a specific conversation.
    """
    tenant_id = resolve_tenant_id(request)
    logger.info(f"Listing messages: tenant_id=%s, conversation_id=%s", tenant_id, conversation_id)

    repo = MessageRepository(request.app.state.db_pool)
    messages = await repo.list_messages(tenant_id=tenant_id, conversation_id=conversation_id)

    return {"data": messages}


@router.post("/send", status_code=status.HTTP_201_CREATED, response_model=SendMessageResponse)
async def send_message(request: Request, data: MessageRequest):
    """
    Send an outbound message to a conversation.
    """
    tenant_id = resolve_tenant_id(request)
    logger.info(f"Sending message: tenant_id=%s, conversation_id=%s", tenant_id, data.conversation_id)

    service = MessagingService(request.app.state.db_pool, ws_manager=manager)

    try:
        message_data = await service.send_outbound_message(
            tenant_id=tenant_id,
            conversation_id=data.conversation_id,
            content=data.content,
        )
        return {
            "status": "success",
            "message": "Message sent and recorded",
            "data": message_data,
        }
    except ValueError as exc:
        logger.warning(f"Validation error sending message: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Internal error sending message: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error processing message",
        )
