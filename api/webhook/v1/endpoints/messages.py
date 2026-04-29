from fastapi import APIRouter, Depends, HTTPException
from app.services.messaging import MessagingService
from app.schemas.message import MessageCreate, MessageResponse # Debes crear estos schemas

router = APIRouter()

@router.post("/send", response_model=MessageResponse)
async def send_message(
    payload: MessageCreate,
    # Aquí inyectarías tu dependencia de servicio
    service: MessagingService = Depends(get_messaging_service) 
):
    try:
        # El payload contendría: conversation_id, text, y tenant_id
        result = await service.send_response(
            conversation_id=payload.conversation_id,
            text=payload.text,
            tenant_id=payload.tenant_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))