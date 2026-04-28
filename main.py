from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from api.webhooks.facebook import router as fb_router
from api.webhooks.whatsapp import router as wa_router

from api.routes.conversations import router as conv_router
from api.routes.messages import router as msg_router

from ws.manager import connect, disconnect
from services.messaging import handle_outgoing_message

from workers.worker import start_worker
import json

app = FastAPI()


# iniciar worker
start_worker()


# routers
app.include_router(fb_router)
app.include_router(wa_router)
app.include_router(conv_router)
app.include_router(msg_router)


@app.get("/")
def home():
    return FileResponse("index.html")


# websocket
@app.websocket("/ws/{conversation_id}")
async def ws_endpoint(ws: WebSocket, conversation_id: int):
    await connect(ws, conversation_id)

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "message":
                await handle_outgoing_message(
                    tenant_id=1,
                    conversation_id=conversation_id,
                    text=msg.get("text")
                )

    except WebSocketDisconnect:
        disconnect(ws, conversation_id)