# app/domain/model.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WebhookMessage(BaseModel):
    """Estandariza el mensaje entrante para tu lógica interna"""
    sender_id: str
    content: str
    timestamp: datetime
    platform: str  # 'facebook', 'instagram', 'whatsapp'