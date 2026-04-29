from abc import ABC, abstractmethod

class BaseChannel(ABC):
    @abstractmethod
    async def send_message(self, recipient_id: str, message_text: str, access_token: str):
        """
        Método obligatorio para enviar mensajes a través de cualquier canal.
        """
        pass