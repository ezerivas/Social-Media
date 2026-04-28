from fastapi import WebSocket

rooms: dict[int, list[WebSocket]] = {}

async def connect(websocket: WebSocket, conversation_id: int):
    await websocket.accept()

    if conversation_id not in rooms:
        rooms[conversation_id] = []

    rooms[conversation_id].append(websocket)


def disconnect(websocket: WebSocket, conversation_id: int):
    if conversation_id in rooms:
        rooms[conversation_id].remove(websocket)


async def send_to_room(conversation_id: int, message: dict):
    if conversation_id in rooms:
        for ws in rooms[conversation_id]:
            await ws.send_json(message)