import os
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from contextlib import asynccontextmanager

from app.api.webhooks import facebook
from app.api.routes import messages
from app.ws.manager import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conexión a la base de datos en Railway
    app.state.db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    print("🚀 Pool de base de datos creado")
    yield
    await app.state.db_pool.close()
    print("💤 Pool cerrado")

app = FastAPI(title="Omnichannel Live", lifespan=lifespan)

# --- RUTAS ---
app.include_router(facebook.router, prefix="/webhooks", tags=["Webhooks"])

@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: int):
    await manager.connect(websocket, tenant_id)

    try:
        # 🔥 mantener conexión viva con ping lógico
        while True:
            try:
                data = await websocket.receive_text()
                print("📩 Recibido:", data)

                # responder algo SIEMPRE
                await manager.broadcast_to_tenant(
                    tenant_id,
                    {
                        "event": "message",
                        "data": data
                    }
                )

            except Exception as inner:
                print("⚠️ Error interno WS:", inner)
                continue

    except Exception as e:
        print("🔴 WS cerrado:", e)

    finally:
        manager.disconnect(websocket, tenant_id)