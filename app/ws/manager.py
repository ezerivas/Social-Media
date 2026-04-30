from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        # {tenant_id: [websockets]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: int) -> None:
        await websocket.accept()
        self.active_connections.setdefault(tenant_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, tenant_id: int) -> None:
        tenant_connections = self.active_connections.get(tenant_id)
        if not tenant_connections:
            return

        try:
            tenant_connections.remove(websocket)
        except ValueError:
            return

        if not tenant_connections:
            self.active_connections.pop(tenant_id, None)

    async def broadcast_to_tenant(self, tenant_id: int, message: dict) -> None:
        tenant_connections = self.active_connections.get(tenant_id)
        if not tenant_connections:
            return

        dead_connections: List[WebSocket] = []
        for connection in tenant_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead_connection in dead_connections:
            self.disconnect(dead_connection, tenant_id)


manager = ConnectionManager()
