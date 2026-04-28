# worker simple (in-memory)

from services.event_bus import subscribe
from workers.handlers.send_message import handle_send


def start_worker():
    def process(event):
        if event["type"] == "send_message":
            handle_send(event)

    subscribe(process)