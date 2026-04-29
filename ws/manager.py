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
            self.active_connections[tenant_id].remove(websocket)

    async def broadcast_to_tenant(self, tenant_id: int, message: dict):
        """Envía el mensaje solo a los operadores conectados de esa empresa específica"""
        if tenant_id in self.active_connections:
            for connection in self.active_connections[tenant_id]:
                await connection.send_json(message)

# Instancia global para ser usada en los servicios
manager = ConnectionManager()