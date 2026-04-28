from services import facebook, instagram, whatsapp


def send_message(channel: str, config: dict, recipient_id: str, text: str):
    if channel == "facebook":
        return facebook.send(config, recipient_id, text)

    elif channel == "instagram":
        return instagram.send(config, recipient_id, text)

    elif channel == "whatsapp":
        return whatsapp.send(config, recipient_id, text)

    else:
        raise ValueError(f"Unsupported channel: {channel}")