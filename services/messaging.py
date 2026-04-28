from repositories.users import get_or_create_user
from repositories.conversations import get_or_create_conversation, update_last_message
from repositories.messages import create_message
from repositories.channels import get_channel_config

from services.channel_router import send_message
from ws.manager import send_to_room


# =========================================================
# 📩 MENSAJE ENTRANTE (Webhook)
# =========================================================
async def handle_incoming_message(
    tenant_id: int,
    channel: str,
    external_user_id: str,
    text: str
):
    """
    Mensaje que viene desde Facebook / IG / WhatsApp
    """

    # 1. Usuario
    user = get_or_create_user(
        tenant_id=tenant_id,
        external_id=external_user_id
    )

    # 2. Conversación
    conversation = get_or_create_conversation(
        tenant_id=tenant_id,
        user_id=user[0],
        channel=channel,
        external_id=external_user_id
    )

    conversation_id = conversation[0]

    # 3. Guardar mensaje
    message = create_message(
        conversation_id=conversation_id,
        role="user",
        content=text
    )

    # 4. Actualizar conversación
    update_last_message(conversation_id)

    # 5. WS realtime
    await send_to_room(conversation_id, {
        "id": message[0],
        "role": message[2],
        "content": message[3],
        "created_at": str(message[4])
    })

    return conversation_id


# =========================================================
# 📤 MENSAJE SALIENTE (Dashboard / WS)
# =========================================================
async def handle_outgoing_message(
    tenant_id: int,
    conversation_id: int,
    text: str
):
    """
    Mensaje enviado desde el dashboard (operador humano)
    """

    # 1. Obtener conversación
    from repositories.conversations import get_conversation_by_id

    conversation = get_conversation_by_id(conversation_id)

    if not conversation:
        raise Exception("Conversation not found")

    channel = conversation["channel"]
    external_id = conversation["external_id"]

    # 2. Config del canal
    config = get_channel_config(tenant_id, channel)

    if not config:
        raise Exception(f"Channel config not found: {channel}")

    # 3. Enviar mensaje (API externa)
    send_message(
        channel=channel,
        config=config,
        recipient_id=external_id,
        text=text
    )

    # 4. Guardar en DB
    message = create_message(
        conversation_id=conversation_id,
        role="assistant",
        content=text
    )

    # 5. Update conversación
    update_last_message(conversation_id)

    # 6. WS realtime
    await send_to_room(conversation_id, {
        "id": message[0],
        "role": message[2],
        "content": message[3],
        "created_at": str(message[4])
    })

    return message