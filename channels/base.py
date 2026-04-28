class BaseChannel:
    def send(self, config: dict, recipient_id: str, text: str):
        raise NotImplementedError