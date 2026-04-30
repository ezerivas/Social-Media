from typing import Any, Dict, Optional

from app.channels.base import BaseChannel
from app.channels.facebook import FacebookChannel
from app.channels.whatsapp import WhatsAppChannel
from app.repositories.messages import MessageRepository


class MessagingService:
    def __init__(self, db_pool, ws_manager=None):
        self.repository = MessageRepository(db_pool)
        self.ws_manager = ws_manager
        self.channels: Dict[str, BaseChannel] = {
            "facebook": FacebookChannel(),
            "whatsapp": WhatsAppChannel(),
        }

    def _get_channel(self, channel_name: str) -> BaseChannel:
        channel = self.channels.get(channel_name)
        if not channel:
            raise ValueError(f"Canal no soportado: {channel_name}")
        return channel

    async def handle_inbound_message(
        self, channel_name: str, payload: Dict[str, Any], tenant_id: int
    ) -> Optional[Dict[str, Any]]:
        channel = self._get_channel(channel_name)
        message_data = channel.parse_webhook(payload)
        if not message_data:
            return None

        saved_message = await self.repository.save_message(
            tenant_id=tenant_id,
            user_external_id=message_data["sender_id"],
            channel=channel_name,
            content=message_data["text"],
            role="user",
        )

        if self.ws_manager:
            await self.ws_manager.broadcast_to_tenant(
                tenant_id,
                {
                    "type": "new_message",
                    "data": saved_message,
                },
            )

        return saved_message

    async def send_outbound_message(self, tenant_id: int, conversation_id: int, content: str):
        conv = await self.repository.get_conversation_details(conversation_id)
        if not conv or conv["tenant_id"] != tenant_id:
            raise ValueError("Conversación no encontrada o acceso denegado")

        channel_name = conv["channel"]
        external_user_id = conv["external_user_id"]
        channel_adapter = self._get_channel(channel_name)

        channel_config = await self.repository.get_channel_config(tenant_id, channel_name)
        if not channel_config:
            raise ValueError(f"Configuración no encontrada para el canal {channel_name}")

        success = await channel_adapter.send_text(
            recipient_id=external_user_id,
            message_text=content,
            config=channel_config,
        )

        if not success:
            return None

        saved_message = await self.repository.save_outbound_message(
            conversation_id=conversation_id,
            content=content,
            role="agent",
        )

        if self.ws_manager:
            await self.ws_manager.broadcast_to_tenant(
                tenant_id,
                {
                    "type": "message_sent",
                    "data": saved_message,
                },
            )

        return saved_message
