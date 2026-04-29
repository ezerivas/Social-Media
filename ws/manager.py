from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Diccionario para separar conexiones por empresa (tenant)
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: int):
        await websocket.accept()
        self.active_connections.setdefault(tenant_id, []).append(websocket)

    async def broadcast_to_tenant(self, tenant_id: int, message: dict):
        # Solo envía a los operadores de la empresa dueña del mensaje
        for connection in self.active_connections.get(tenant_id, []):
            await connection.send_json(message)

manager = ConnectionManager()