"""
WhatsApp channel implementation (placeholder).
"""
import logging
from typing import Any, Dict, Optional

from app.channels.base import BaseChannel

logger = logging.getLogger(__name__)


class WhatsAppChannel(BaseChannel):
    """WhatsApp Business API channel adapter."""

    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse WhatsApp webhook payload.
        TODO: Implement when WhatsApp integration is added.
        """
        logger.debug("WhatsApp webhook received: %s", payload)
        return None

    async def send_text(
        self,
        recipient_id: str,
        message_text: str,
        config: Dict[str, Any],
    ) -> bool:
        """
        Send a text message via WhatsApp Business API.
        TODO: Implement when WhatsApp integration is added.
        """
        logger.warning("WhatsApp send not implemented")
        raise NotImplementedError("WhatsApp integration not yet implemented")
