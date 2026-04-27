from repositories.users import get_or_create_user
from repositories.conversations import get_or_create_conversation
from repositories.messages import save_message


# Maneja mensaje entrante
def handle_incoming_message(sender_id: str, text: str, name: str = None):

    user_id = get_or_create_user(sender_id, name)

    conversation_id = get_or_create_conversation(user_id)

    save_message(conversation_id, "user", text)

    return conversation_id