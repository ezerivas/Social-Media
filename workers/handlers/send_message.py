from services.channel_router import get_driver
from services.channel_config import resolve_channel_config
from repositories.conversations import get_conversation


def handle_send(event: dict):
    conversation = get_conversation(event["conversation_id"])

    channel = conversation["channel"]
    recipient = conversation["external_user_id"]

    driver = get_driver(channel)
    config = resolve_channel_config(channel)

    driver.send(config, recipient, event["text"])