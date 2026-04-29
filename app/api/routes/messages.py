from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from app.services.messaging import MessagingService

router = APIRouter()

class MessageRequest(BaseModel):
    conversation_id: int
    content: str

@router.post("/send")
async def send_message(req: Request, data: MessageRequest):
    """Endpoint que llama el Dashboard para enviar una respuesta"""
    # El tenant_id debería venir del token JWT o del resolver
    tenant_id = req.state.tenant_id 
    
    service = MessagingService(req.app.state.db_pool)
    
    try:
        message = await service.send_outbound_message(
            tenant_id=tenant_id,
            conversation_id=data.conversation_id,
            content=data.content
        )
        return {"status": "sent", "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))