from fastapi import APIRouter
from repositories.conversations import get_all_conversations

router = APIRouter()


@router.get("/conversations")
def conversations():
    return get_all_conversations()