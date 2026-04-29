@router.post("/send")
async def send_message(payload: MessageCreate, service: MessagingService = Depends()):
    # Simplemente delega la complejidad al servicio
    return await service.send_response(
        payload.conversation_id, 
        payload.text, 
        payload.tenant_id
    )