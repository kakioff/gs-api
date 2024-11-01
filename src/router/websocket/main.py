from fastapi import Depends, Query, WebSocket, WebSocketDisconnect
from redis import Redis

from database import get_redis
from . import router
from .models import ConnectManager


manager = ConnectManager()


@router.websocket("")
async def ws_endpoint(
    websocket: WebSocket,
    redis: Redis = Depends(get_redis),
    client_id: str = Query(),
    room_id: str = Query(default=None),
):
    await manager.connect(websocket, client_id, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        # await manager.broadcast(f"{websocket.client.host} left the chat")
