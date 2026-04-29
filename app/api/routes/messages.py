from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel
from app.services.messaging import MessagingService

router = APIRouter()

class MessageRequest(BaseModel):
    conversation_id: int
    content: str

@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_message(req: Request, data: MessageRequest):
    """
    Endpoint que llama el Dashboard para enviar una respuesta manual.
    Flujo: API -> MessagingService -> Channel Adapter (FB/WA) -> DB -> WebSocket
    """
    
    # 1. Recuperar tenant_id (inyectado por tu middleware de seguridad/tenant)
    tenant_id = getattr(req.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Tenant no identificado"
        )
    
    # 2. Instanciar el servicio con el pool de la app
    # Nota: También podrías pasarle el ws_manager si quieres notificar desde el servicio
    service = MessagingService(req.app.state.db_pool)
    
    try:
        # 3. El servicio se encarga de:
        # - Buscar el canal de esa conversación.
        # - Recuperar tokens de la DB.
        # - Enviar a la API de Meta (Facebook/WhatsApp).
        # - Guardar en la tabla 'messages' con role='agent'.
        message_data = await service.send_outbound_message(
            tenant_id=tenant_id,
            conversation_id=data.conversation_id,
            content=data.content
        )
        
        # 4. Notificar vía WebSockets (Opcional aquí, o dentro del Service)
        # Esto asegura que si el agente tiene otra pestaña abierta, vea su propio mensaje enviado.
        if hasattr(req.app.state, "ws_manager"):
            await req.app.state.ws_manager.broadcast_to_tenant(
                tenant_id, 
                {
                    "event": "new_message",
                    "data": message_data
                }
            )

        return {
            "status": "success", 
            "message": "Mensaje enviado y registrado",
            "data": message_data
        }

    except ValueError as ve:
        # Errores de lógica (ej. conversación no encontrada o canal no configurado)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Errores técnicos (ej. caída de la API de Meta)
        print(f"Error crítico en send_message: {str(e)}") # Log para debug
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al procesar el envío")