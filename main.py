import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncpg
from app.api.webhooks import facebook  # Importaremos tu router de webhook

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conexión al pool de la base de datos al iniciar
    app.state.db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    print("🚀 Pool de base de datos conectado")
    yield
    # Cerrar conexión al apagar
    await app.state.db_pool.close()
    print("💤 Conexión a base de datos cerrada")

app = FastAPI(title="Omnichannel API", lifespan=lifespan)

# Incluimos los routers de los webhooks
app.include_router(facebook.router, prefix="/webhooks", tags=["Meta"])

@app.get("/")
async def health_check():
    return {"status": "online", "message": "API de mensajería operativa"}