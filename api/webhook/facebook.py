from fastapi import APIRouter, Request, Query, HTTPException
import os

router = APIRouter()

VERIFY_TOKEN = os.getenv("FACEBOOK_TOKEN")

@router.get("/facebook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")

@router.post("/facebook")
async def handle_messages(request: Request):
    payload = await request.json()
    # Aquí iría tu lógica para enviar al Worker o Repository
    print(f"Mensaje recibido: {payload}")
    return {"status": "ok"}