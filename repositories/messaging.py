from repositories.users import get_user_by_external_id, create_user
from repositories.conversations import get_conversation_by_user, create_conversation
from repositories.messages import insert_message
from meta import get_user_name

def handle_incoming_message(external_id, text, sender="user"):
    user = get_user_by_external_id(external_id)

    if not user:
        name = get_user_name(external_id)
        user = create_user(external_id, name)

    conv = get_conversation_by_user(user["id"])

    if not conv:
        conv = create_conversation(user["id"], external_id)

    insert_message(conv["id"], sender, text)

    return conv["id"]