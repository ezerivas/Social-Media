from fastapi import APIRouter, Request, HTTPException, Depends
from app.repositories.messages import MessageRepository
import os

router = APIRouter()

# Dependencia para obtener el repositorio
async def get_repo(request: Request):
    return MessageRepository(request.app.state.db_pool)

@router.post("/facebook")
async def handle_facebook_events(request: Request, repo: MessageRepository = Depends(get_repo)):
    payload = await request.json()
    
    try:
        # 1. Extraer datos básicos del JSON de Meta (Simplificado para la prueba)
        # Meta envía los mensajes en entry -> messaging
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event.get("message", {}).get("text")
                
                if message_text:
                    # 2. Lógica Multi-tenant inicial:
                    # Buscamos o creamos la conversación para el tenant 1 (el 'default' que creamos)
                    conv_id = await repo.get_or_create_conversation(
                        tenant_id=1, 
                        user_id=1, # Usuario genérico inicial
                        channel="facebook",
                        external_user_id=sender_id
                    )
                    
                    # 3. Guardar el mensaje
                    await repo.create_message(
                        conversation_id=conv_id,
                        role="user",
                        content=message_text
                    )
                    print(f"✅ Mensaje guardado en DB: {message_text}")

        return {"status": "success"}
    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")
        return {"status": "error", "message": str(e)}