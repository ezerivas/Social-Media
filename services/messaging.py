from repositories.users import get_or_create_user
from repositories.conversations import get_or_create_conversation, update_last_message
from repositories.messages import create_message


def handle_incoming_message(user_external_id: str, text: str):
    user = get_or_create_user(user_external_id)

    conversation = get_or_create_conversation(user[0])

    create_message(conversation[0], "user", text)

    reply = "ok"

    create_message(conversation[0], "assistant", reply)

    update_last_message(conversation[0])

    return reply