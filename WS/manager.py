from fastapi import WebSocket

rooms = {}


async def connect(ws: WebSocket, conversation_id: int):
    await ws.accept()

    rooms.setdefault(conversation_id, []).append(ws)


def disconnect(ws: WebSocket, conversation_id: int):
    rooms.get(conversation_id, []).remove(ws)


async def send_to_room(conversation_id: int, message: dict):
    for ws in rooms.get(conversation_id, []):
        await ws.send_json(message)