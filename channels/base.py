from abc import ABC, abstractmethod

class IBaseChannel(ABC):
    @abstractmethod
    async def send_text(self, to_external_id: str, message_text: str, config: dict) -> str:
        pass