"""
Messaging service for handling inbound and outbound messages.
"""
import logging
from typing import Any, Dict, Optional

from app.channels.base import BaseChannel
from app.channels.facebook import FacebookChannel
from app.channels.whatsapp import WhatsAppChannel
from app.repositories.messages import MessageRepository

logger = logging.getLogger(__name__)


class MessagingService:
    """Service for handling messaging operations across channels."""

    # Channel implementations
    CHANNELS: Dict[str, BaseChannel] = {
        "facebook": FacebookChannel(),
        "whatsapp": WhatsAppChannel(),
    }

    def __init__(self, db_pool, ws_manager=None):
        self.repository = MessageRepository(db_pool)
        self.ws_manager = ws_manager

    def _get_channel(self, channel_name: str) -> BaseChannel:
        """Get channel implementation by name."""
        channel = self.CHANNELS.get(channel_name)
        if not channel:
            available = ", ".join(self.CHANNELS.keys())
            raise ValueError(f"Unsupported channel: {channel_name}. Available: {available}")
        return channel

    async def handle_inbound_message(
        self,
        channel_name: str,
        payload: Dict[str, Any],
        tenant_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Handle an inbound message from a channel webhook.
        """
        logger.info("Handling inbound message: channel=%s, tenant_id=%s", channel_name, tenant_id)

        channel = self._get_channel(channel_name)
        message_data = channel.parse_webhook(payload)

        if not message_data:
            logger.debug("No message data parsed from webhook payload")
            return None

        # Save message to database
        saved_message = await self.repository.save_message(
            tenant_id=tenant_id,
            user_external_id=message_data["sender_id"],
            channel=channel_name,
            content=message_data["text"],
            role="user",
        )

        logger.info("Inbound message saved: conversation_id=%s", saved_message.get("conversation_id"))

        # Broadcast to connected WebSocket clients
        if self.ws_manager:
            await self.ws_manager.broadcast_to_tenant(
                tenant_id,
                {
                    "type": "new_message",
                    "data": saved_message,
                },
            )

        return saved_message

    async def send_outbound_message(
        self,
        tenant_id: int,
        conversation_id: int,
        content: str,
    ) -> Dict[str, Any]:
        """
        Send an outbound message to a conversation.
        """
        logger.info("Sending outbound message: tenant_id=%s, conversation_id=%s", tenant_id, conversation_id)

        # Verify conversation exists and belongs to tenant
        conv = await self.repository.get_conversation_details(conversation_id)
        if not conv or conv["tenant_id"] != tenant_id:
            raise ValueError("Conversation not found or access denied")

        channel_name = conv["channel"]
        external_user_id = conv["external_user_id"]

        # Get channel adapter
        channel_adapter = self._get_channel(channel_name)

        # Get channel configuration (optional)
        channel_config = await self.repository.get_channel_config(tenant_id, channel_name)

        # Try to send via channel adapter (if config exists)
        send_success = False
        if channel_config:
            try:
                send_success = await channel_adapter.send_text(
                    recipient_id=external_user_id,
                    message_text=content,
                    config=channel_config,
                )
            except Exception as e:
                logger.warning("Failed to send via channel adapter: %s", e)
        else:
            logger.warning("No channel config found, skipping external send")
            send_success = True  # Allow saving without external send

        if not send_success:
            logger.error("Failed to send message via channel adapter")
            return None

        # Save outbound message to database
        saved_message = await self.repository.save_outbound_message(
            conversation_id=conversation_id,
            content=content,
            role="agent",
        )

        logger.info("Outbound message saved: message_id=%s", saved_message.get("id"))

        # Broadcast to connected WebSocket clients
        if self.ws_manager:
            await self.ws_manager.broadcast_to_tenant(
                tenant_id,
                {
                    "type": "message_sent",
                    "data": saved_message,
                },
            )

        return saved_message
