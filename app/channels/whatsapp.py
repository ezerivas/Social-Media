from typing import Any, Dict, Optional

from app.channels.base import BaseChannel


class WhatsAppChannel(BaseChannel):
    """Placeholder para futura integración de WhatsApp."""

    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

    async def send_text(self, recipient_id: str, message_text: str, config: Dict[str, Any]) -> bool:
        raise NotImplementedError("WhatsAppChannel aún no implementado")
