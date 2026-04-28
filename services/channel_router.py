from channels.facebook import FacebookChannel
from channels.instagram import InstagramChannel
from channels.whatsapp import WhatsAppChannel


def get_driver(channel: str):
    if channel == "facebook":
        return FacebookChannel()

    if channel == "instagram":
        return InstagramChannel()

    if channel == "whatsapp":
        return WhatsAppChannel()

    raise ValueError("unsupported channel")