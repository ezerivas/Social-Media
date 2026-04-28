from fastapi import APIRouter
from repositories.messages import get_messages_by_conversation

router = APIRouter()


@router.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int):
    return get_messages_by_conversation(conversation_id)