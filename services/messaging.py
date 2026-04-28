from repositories.users import get_or_create_user
from repositories.conversations import get_or_create_conversation, update_last_message
from repositories.messages import create_message


def handle_incoming_message(user_external_id: str, text: str):
    user = get_or_create_user(user_external_id)

    conversation = get_or_create_conversation(user[0], user_external_id)

    create_message(conversation[0], "user", text)

    update_last_message(conversation[0])

    return conversation