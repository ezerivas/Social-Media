# simplificado (luego DB por tenant)

from core.config import (
    FACEBOOK_TOKEN,
    INSTAGRAM_TOKEN,
    WHATSAPP_TOKEN
)


def resolve_channel_config(channel: str):
    if channel == "facebook":
        return {"token": FACEBOOK_TOKEN}

    if channel == "instagram":
        return {"token": INSTAGRAM_TOKEN}

    if channel == "whatsapp":
        return {"token": WHATSAPP_TOKEN}

    raise ValueError("missing config")