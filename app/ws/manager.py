from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Diccionario para organizar conexiones por tenant_id: {tenant_id: [list_of_websockets]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: int):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = []
        self.active_connections[tenant_id].append(websocket)

    def disconnect(self, websocket: WebSocket, tenant_id: int):
        if tenant_id in self.active_connections:
            try:
                self.active_connections[tenant_id].remove(websocket)
            except ValueError:
                pass
async def broadcast_to_tenant(self, tenant_id: int, message: dict):
    if tenant_id not in self.active_connections:
        return

    dead_connections = []

    for connection in self.active_connections[tenant_id]:
        try:
            await connection.send_json(message)
        except Exception:
            dead_connections.append(connection)

    # limpiar conexiones muertas
    for dc in dead_connections:
        self.active_connections[tenant_id].remove(dc)

# Instancia global para ser usada en los servicios
manager = ConnectionManager()