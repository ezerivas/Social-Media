from models import User, Conversation, Message
from datetime import datetime


def save_message(db, sender_id: str, text: str, sender="user"):
    # buscar usuario
    user = db.query(User).filter(User.external_id == sender_id).first()

    if not user:
        user = User(external_id=sender_id, canal="facebook")
        db.add(user)
        db.commit()
        db.refresh(user)

    # buscar conversación
    conv = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).first()

    if not conv:
        conv = Conversation(user_id=user.id, canal="facebook")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # guardar mensaje
    message = Message(
        conversation_id=conv.id,
        sender=sender,
        text=text
    )

    db.add(message)
    conv.last_message_at = datetime.utcnow()

    db.commit()