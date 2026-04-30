from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel

from app.repositories.messages import MessageRepository
from app.services.messaging import MessagingService
from app.ws.manager import manager

router = APIRouter()


class MessageRequest(BaseModel):
    conversation_id: int
    content: str


def resolve_tenant_id(req: Request) -> int:
    return getattr(req.state, "tenant_id", 1)


@router.get("/channels")
async def list_channels():
    return [
        {"id": "facebook", "name": "Facebook", "enabled": True},
        {"id": "instagram", "name": "Instagram", "enabled": False},
        {"id": "whatsapp", "name": "WhatsApp", "enabled": False},
    ]


@router.get("/conversations")
async def list_conversations(req: Request, channel: str = Query(...)):
    tenant_id = resolve_tenant_id(req)
    repo = MessageRepository(req.app.state.db_pool)
    conversations = await repo.list_conversations(tenant_id=tenant_id, channel=channel)
    return {"data": conversations}


@router.get("/conversations/{conversation_id}/messages")
async def list_conversation_messages(req: Request, conversation_id: int):
    tenant_id = resolve_tenant_id(req)
    repo = MessageRepository(req.app.state.db_pool)
    messages = await repo.list_messages(tenant_id=tenant_id, conversation_id=conversation_id)
    return {"data": messages}


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_message(req: Request, data: MessageRequest):
    tenant_id = resolve_tenant_id(req)
    service = MessagingService(req.app.state.db_pool, ws_manager=manager)

    try:
        message_data = await service.send_outbound_message(
            tenant_id=tenant_id,
            conversation_id=data.conversation_id,
            content=data.content,
        )
        return {
            "status": "success",
            "message": "Mensaje enviado y registrado",
            "data": message_data,
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar el envío",
        )
