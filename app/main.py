from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, WebSocket

from app.api.routes import messages
from app.api.webhooks import facebook
from app.core.config import settings
from app.ws.manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = settings.DATABASE_URL
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurada")

    app.state.db_pool = await asyncpg.create_pool(database_url)
    yield
    await app.state.db_pool.close()


app = FastAPI(title="Omnichannel Live", lifespan=lifespan)

app.include_router(facebook.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])


@app.get("/health")
async def health():
    return {"ok": True}


@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: int):
    await manager.connect(websocket, tenant_id)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_to_tenant(
                tenant_id,
                {
                    "event": "message",
                    "data": data,
                },
            )
    finally:
        manager.disconnect(websocket, tenant_id)
