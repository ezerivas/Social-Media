import os
import asyncpg
from fastapi import FastAPI, Request, Query, HTTPException
from contextlib import asynccontextmanager

# 1. Gestión del ciclo de vida (Conexión a DB)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto se ejecuta al arrancar la app en Railway
    app.state.db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    print("Conexión a PostgreSQL establecida")
    yield
    # Esto se ejecuta al apagar la app
    await app.state.db_pool.close()
    print("Conexión a PostgreSQL cerrada")

app = FastAPI(lifespan=lifespan)

# --- RUTAS DE PRUEBA ---

@app.get("/")
async def root():
    return {"message": "Omnichannel API is running!"}

# --- WEBHOOK DE FACEBOOK/WHATSAPP ---

VERIFY_TOKEN = os.getenv("FACEBOOK_TOKEN")

@app.get("/webhook")
async def verify_facebook_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """Ruta obligatoria para que Meta valide tu servidor"""
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado con éxito")
        return int(challenge)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")

@app.post("/webhook")
async def handle_facebook_events(request: Request):
    """Ruta donde llegarán los mensajes reales"""
    payload = await request.json()
    
    # Por ahora solo imprimimos en logs de Railway para validar
    print(f"📩 Evento recibido: {payload}")
    
    # Aquí es donde más adelante llamarás a tu Repository para 
    # hacer el INSERT INTO messages...
    
    return {"status": "EVENT_RECEIVED"}