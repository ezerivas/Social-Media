from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseChannel(ABC):
    @abstractmethod
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normaliza payload inbound a un formato común."""

    @abstractmethod
    async def send_text(self, recipient_id: str, message_text: str, config: Dict[str, Any]) -> bool:
        """Envía un mensaje outbound al proveedor."""
