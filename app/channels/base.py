"""
Base channel interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseChannel(ABC):
    """Abstract base class for channel implementations."""

    @abstractmethod
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize inbound webhook payload to common format.

        Args:
            payload: Raw webhook payload from provider

        Returns:
            Normalized message data or None if no valid message
        """

    @abstractmethod
    async def send_text(
        self,
        recipient_id: str,
        message_text: str,
        config: Dict[str, Any],
    ) -> bool:
        """
        Send an outbound message via the channel provider.

        Args:
            recipient_id: Recipient identifier
            message_text: Message content
            config: Channel configuration

        Returns:
            True if sent successfully
        """
