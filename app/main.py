"""
Main entry point for the Omnichannel Live API.
"""
import logging
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

from app.api.routes import messages
from app.api.webhooks import facebook
from app.core.config import settings
from app.ws.manager import manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - database connection pool."""
    database_url = settings.DATABASE_URL
    if not database_url:
        logger.error("DATABASE_URL not configured")
        raise RuntimeError("DATABASE_URL is required")

    logger.info("Creating database connection pool")
    app.state.db_pool = await asyncpg.create_pool(database_url)
    logger.info("Database pool created successfully")

    yield

    logger.info("Closing database connection pool")
    await app.state.db_pool.close()
    logger.info("Database pool closed")


app = FastAPI(
    title="Omnichannel Live API",
    description="Unified messaging platform for multiple channels",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(facebook.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "omnichannel-live"}


@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: int):
    """WebSocket endpoint for real-time messaging."""
    await manager.connect(websocket, tenant_id)
    logger.info(f"WebSocket connected: tenant_id={tenant_id}")

    try:
        while True:
            # Keep connection alive and detect disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected: tenant_id=%s", tenant_id)
    finally:
        manager.disconnect(websocket, tenant_id)
        logger.info(f"WebSocket disconnected: tenant_id={tenant_id}")
