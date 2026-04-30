"""
WebSocket connection manager for real-time messaging.
"""
import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per tenant."""

    def __init__(self):
        # {tenant_id: [websockets]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: int) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.setdefault(tenant_id, []).append(websocket)
        logger.info("WebSocket connected: tenant_id=%s, total=%s", tenant_id, len(self.active_connections.get(tenant_id, [])))

    def disconnect(self, websocket: WebSocket, tenant_id: int) -> None:
        """Remove a WebSocket connection."""
        tenant_connections = self.active_connections.get(tenant_id)
        if not tenant_connections:
            return

        try:
            tenant_connections.remove(websocket)
            logger.debug("WebSocket removed: tenant_id=%s", tenant_id)
        except ValueError:
            pass

        if not tenant_connections:
            self.active_connections.pop(tenant_id, None)
            logger.debug("No more connections for tenant_id=%s", tenant_id)

    async def broadcast_to_tenant(self, tenant_id: int, message: dict) -> None:
        """Broadcast a message to all connected clients for a tenant."""
        tenant_connections = self.active_connections.get(tenant_id)
        if not tenant_connections:
            logger.debug("No connections to broadcast: tenant_id=%s", tenant_id)
            return

        dead_connections: List[WebSocket] = []
        for connection in tenant_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning("Failed to send to connection: %s", e)
                dead_connections.append(connection)

        # Clean up dead connections
        for dead_connection in dead_connections:
            self.disconnect(dead_connection, tenant_id)


# Singleton instance
manager = ConnectionManager()
