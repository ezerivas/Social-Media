from app.repositories.messages import MessageRepository
from app.channels.facebook import FacebookChannel
from app.ws.manager import manager

class MessagingService:
    def __init__(self, repo: MessageRepository):
        self.repo = repo
        self.fb_channel = FacebookChannel()

    async def send_response(self, conversation_id: int, text: str, tenant_id: int):
        # 1. Obtiene recipient_id y tokens de la DB
        details = await self.repo.get_conversation_details(conversation_id)
        
        # 2. Envía físicamente a la API de Meta
        external_id = await self.fb_channel.send_text(
            to_external_id=details['external_user_id'],
            message_text=text,
            config=details['config'] # JSON con el access_token
        )

        # 3. Guarda el mensaje del agente en la tabla 'messages'
        new_msg_id = await self.repo.create_message(
            conversation_id=conversation_id,
            role="agent",
            content=text,
            external_id=external_id
        )

        # 4. Notifica al Dashboard por WebSocket (Real-time)
        await manager.broadcast_to_tenant(tenant_id, {
            "event": "new_message",
            "data": {"id": new_msg_id, "content": text, "role": "agent"}
        })
        
        return {"id": new_msg_id, "external_id": external_id}