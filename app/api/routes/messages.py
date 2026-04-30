from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.services.messaging import MessagingService
from app.ws.manager import manager

router = APIRouter()


class MessageRequest(BaseModel):
    conversation_id: int
    content: str


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_message(req: Request, data: MessageRequest):
    tenant_id = getattr(req.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant no identificado",
        )

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
