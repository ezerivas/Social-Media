from app.repositories.messages import MessageRepository
from app.channels.facebook import FacebookChannel
from app.ws.manager import manager

class MessagingService:
    def __init__(self, db_pool):
        self.repo = MessageRepository(db_pool)

    async def handle_inbound_message(self, tenant_id: int, external_user_id: str, content: str, channel: str):
        """Maneja mensajes que vienen de APIs externas (Facebook/WA)"""
        # 1. Obtener o crear conversación (asumimos user_id 1 para pruebas o resolvemos por external_id)
        conv_id = await self.repo.get_or_create_conversation(
            tenant_id=tenant_id, 
            user_id=1, 
            channel=channel, 
            external_user_id=external_user_id
        )
        
        # 2. Guardar mensaje del cliente
        message = await self.repo.save_message(conv_id, 'customer', content)
        
        # 3. Notificar al Dashboard vía WebSocket
        await manager.broadcast_to_tenant(tenant_id, {
            "event": "new_message",
            "data": message
        })
        return message

    async def send_outbound_message(self, tenant_id: int, conversation_id: int, content: str):
        """Maneja respuestas enviadas por el agente desde el Dashboard"""
        # 1. Obtener config del canal para tener el token
        conv_data = await self.repo.get_conversation_with_config(conversation_id)
        if not conv_data:
            raise Exception("Conversación no encontrada")

        # 2. Enviar a la API externa
        if conv_data['channel'] == 'facebook':
            fb_config = conv_data['config']
            channel_api = FacebookChannel(
                access_token=fb_config['access_token'],
                page_id=fb_config['page_id']
            )
            await channel_api.send_text(conv_data['external_user_id'], content)

        # 3. Guardar en DB con rol 'agent'
        message = await self.repo.save_message(conversation_id, 'agent', content)

        # 4. Notificar a otros posibles operadores conectados
        await manager.broadcast_to_tenant(tenant_id, {
            "event": "message_sent",
            "data": message
        })
        return message