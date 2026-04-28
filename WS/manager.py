from fastapi import WebSocket

rooms = {}


async def connect(ws: WebSocket, conversation_id: int):
    await ws.accept()
    rooms.setdefault(conversation_id, []).append(ws)


def disconnect(ws: WebSocket, conversation_id: int):
    rooms[conversation_id].remove(ws)


async def broadcast(conversation_id: int, data: dict):
    for ws in rooms.get(conversation_id, []):
        await ws.send_json(data)