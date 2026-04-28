# cerebro del sistema

from repositories.users import get_or_create_user
from repositories.conversations import get_or_create_conversation, update_last_message
from repositories.messages import create_message

from services.channel_router import get_driver
from services.channel_config import resolve_channel_config
from services.event_bus import publish

from ws.manager import send_to_room


async def handle_incoming_message(tenant_id: int, channel: str, external_user_id: str, text: str):
    user = get_or_create_user(tenant_id, external_user_id)

    conversation = get_or_create_conversation(
        tenant_id,
        user[0],
        channel,
        external_user_id
    )

    create_message(conversation[0], "user", text)
    update_last_message(conversation[0])

    # realtime
    await send_to_room(conversation[0], {
        "role": "user",
        "content": text
    })


async def handle_outgoing_message(tenant_id: int, conversation_id: int, text: str):
    message = create_message(conversation_id, "assistant", text)
    update_last_message(conversation_id)

    # evento async (envío externo)
    publish({
        "type": "send_message",
        "tenant_id": tenant_id,
        "conversation_id": conversation_id,
        "text": text
    })

    # realtime
    await send_to_room(conversation_id, {
        "id": message[0],
        "role": message[2],
        "content": message[3]
    })